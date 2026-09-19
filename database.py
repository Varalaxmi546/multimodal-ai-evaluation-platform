import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "platform.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_type TEXT NOT NULL,
            prompt TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def to_text(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2)


def save_analysis(analysis_type, prompt, result):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO analyses (analysis_type, prompt, result) VALUES (?, ?, ?)",
        (to_text(analysis_type), to_text(prompt), to_text(result)),
    )
    conn.commit()
    item_id = cur.lastrowid
    conn.close()
    return item_id


def get_history():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, analysis_type, prompt, result, created_at
        FROM analyses ORDER BY id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_analysis(item_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, analysis_type, prompt, result, created_at FROM analyses WHERE id=?",
        (item_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_analysis(item_id):
    conn = get_connection()
    cur = conn.execute("DELETE FROM analyses WHERE id=?", (item_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def delete_all_history():
    conn = get_connection()
    conn.execute("DELETE FROM analyses")
    conn.commit()
    conn.close()


def get_dashboard_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
    evaluations = conn.execute(
        """
        SELECT COUNT(*) FROM analyses
        WHERE analysis_type IN ('Model Evaluation','Automatic Model Evaluation')
        """
    ).fetchone()[0]
    text_count = conn.execute(
        "SELECT COUNT(*) FROM analyses WHERE analysis_type='Text Analysis'"
    ).fetchone()[0]
    image_count = conn.execute(
        "SELECT COUNT(*) FROM analyses WHERE analysis_type='Image Analysis'"
    ).fetchone()[0]
    pdf_count = conn.execute(
        "SELECT COUNT(*) FROM analyses WHERE analysis_type='PDF Analysis'"
    ).fetchone()[0]
    conn.close()
    return {
        "total_analyses": total,
        "total_evaluations": evaluations,
        "text_analyses": text_count,
        "image_analyses": image_count,
        "pdf_analyses": pdf_count,
    }
