from typing import Dict, List, Any
import sqlite3
from datetime import datetime

class ContextManager:
    def __init__(self, db_path: str = "context.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contexts (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                conversation_id TEXT,
                content TEXT,
                timestamp DATETIME,
                embedding BLOB
            )
        """)
        conn.commit()
        conn.close()
    
    def save_context(self, topic: str, conversation_id: str, content: str):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO contexts (topic, conversation_id, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (topic, conversation_id, content, datetime.now()))
        conn.commit()
        conn.close()
    
    def get_context(self, topic: str = None, conversation_id: str = None) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        if topic:
            results = conn.execute("""
                SELECT * FROM contexts WHERE topic = ? ORDER BY timestamp DESC
            """, (topic,)).fetchall()
        elif conversation_id:
            results = conn.execute("""
                SELECT * FROM contexts WHERE conversation_id = ? ORDER BY timestamp DESC
            """, (conversation_id,)).fetchall()
        else:
            results = conn.execute("""
                SELECT * FROM contexts ORDER BY timestamp DESC LIMIT 10
            """).fetchall()
        conn.close()
        return [dict(zip(['id', 'topic', 'conversation_id', 'content', 'timestamp', 'embedding'], row)) for row in results]
