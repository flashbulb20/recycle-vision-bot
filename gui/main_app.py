# gui/main_app.py

from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QWidget, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from utils.file_handler import get_image_file
from api.open_api import get_image_description
from db.db_handler import init_db, save_log, search_logs
from logic.action_mapper import map_action  # 분류 결과 -> 로봇 동작 추론
import os

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("재활용 쓰레기 이미지 분류기")
        self.setGeometry(100, 100, 900, 700)

        init_db()
        self.image_path = None

        # 이미지 미리보기
        self.image_label = QLabel("이미지를 선택하세요")
        self.image_label.setFixedSize(300, 300)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")

        # 버튼
        self.load_button = QPushButton("이미지 열기")
        self.generate_button = QPushButton("설명 생성")
        self.save_button = QPushButton("DB 저장")
        self.save_button.setEnabled(False)

        # 입력/출력 위젯
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("추가 프롬프트 입력")

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어 입력")
        self.search_button = QPushButton("검색")

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["분류", "동작", "설명 요약", "시간"])

        # 레이아웃
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.image_label)
        top_layout.addWidget(self.load_button)

        middle_layout = QVBoxLayout()
        middle_layout.addWidget(self.text_input)
        middle_layout.addWidget(self.generate_button)
        middle_layout.addWidget(self.save_button)
        middle_layout.addWidget(self.result_output)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(middle_layout)
        layout.addLayout(search_layout)
        layout.addWidget(self.result_table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 이벤트 연결
        self.load_button.clicked.connect(self.load_image)
        self.generate_button.clicked.connect(self.generate_description)
        self.save_button.clicked.connect(self.save_result)
        self.search_button.clicked.connect(self.search_result)

    def load_image(self):
        path = get_image_file()
        if path:
            self.image_path = path
            self.image_label.setPixmap(
                QLabel().pixmap().fromImage(path).scaled(300, 300, Qt.KeepAspectRatio)
            )

    def generate_description(self):
        if not self.image_path:
            QMessageBox.warning(self, "이미지 없음", "이미지를 먼저 선택해주세요.")
            return

        prompt = self.text_input.toPlainText()
        result = get_image_description(self.image_path, prompt)
        if result.startswith("api 호출 오류"):
            QMessageBox.critical(self, "API 오류", result)
            return

        # category, action 추출
        self.result_output.setPlainText(result)
        self.category = self.extract_category(result)
        self.action = map_action(self.category, result)
        self.save_button.setEnabled(True)

    def extract_category(self, text):
        for keyword in ["플라스틱", "종이", "유리", "캔", "일반쓰레기"]:
            if keyword in text:
                return keyword
        return "미분류"

    def save_result(self):
        if not hasattr(self, "category") or not self.image_path:
            QMessageBox.warning(self, "저장 불가", "먼저 설명을 생성해주세요.")
            return

        save_log(
            image_path=self.image_path,
            category=self.category,
            description=self.result_output.toPlainText(),
            action=self.action
        )

        QMessageBox.information(self, "저장 완료", "분류 결과가 DB에 저장되었습니다.")
        self.save_button.setEnabled(False)

    def search_result(self):
        keyword = self.search_input.text().strip()
        results = search_logs(keyword)

        self.result_table.setRowCount(0)
        for row_data in results:
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            self.result_table.setItem(row, 0, QTableWidgetItem(row_data[1]))  # category
            self.result_table.setItem(row, 1, QTableWidgetItem(row_data[2]))  # action
            self.result_table.setItem(row, 2, QTableWidgetItem(row_data[3][:50]))  # description 요약
            self.result_table.setItem(row, 3, QTableWidgetItem(row_data[4]))  # created_at