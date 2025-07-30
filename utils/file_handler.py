# file: utils/file_handler.py

from PyQt5.QtWidgets import QFileDialog
import base64
import os

def get_image_file():
    """
    PyQt 파일 다이얼로그를 통해 이미지 파일 경로 선택
    :return: 선택된 이미지 파일 경로 or None
    """
    path, _ = QFileDialog.getOpenFileName(
        None,
        '이미지 선택',
        '',
        'Images (*.png *.jpg *.jpeg *.bmp *.gif)'
    )
    return path if path and os.path.exists(path) else None


def encode_image_to_base64(image_path):
    """
    이미지 파일을 base64 문자열로 인코딩
    :param image_path: 이미지 파일 경로
    :return: base64 인코딩된 문자열
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"이미지 인코딩 실패: {e}")
