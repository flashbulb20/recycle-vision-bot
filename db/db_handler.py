import sqlite3
from utils.config import DB_PATH

def init_db():
    """DB 초기화 - 테이블이 없으면 생성"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            action TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def save_log(image_path: str, category: str, description: str, action: str):
    """분석 결과 저장"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO logs (image_path, category, description, action)
        VALUES (?, ?, ?, ?)
    ''', (image_path, category, description, action))
    conn.commit()
    conn.close()


def search_logs(keyword: str):
    """키워드(분류/설명/동작 포함)로 검색"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        SELECT image_path, category, action, description, created_at
        FROM logs
        WHERE category LIKE ? OR description LIKE ? OR action LIKE ?
        ORDER BY created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    rows = cur.fetchall()
    conn.close()
    return rows
