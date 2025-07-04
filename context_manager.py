from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from typing import List, Dict, Any
import sqlite3

Base = declarative_base()

class Context(Base):
    __tablename__ = 'contexts'
    id = Column(Integer, primary_key=True)
    topic = Column(String)
    conversation_id = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    embedding = Column(LargeBinary, nullable=True)

class ContextManager:
    def __init__(self, db_url: str = 'sqlite:///context.db'):
        self.engine = create_engine(db_url, pool_pre_ping=True, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_context(self, topic: str, conversation_id: str, content: str, embedding: bytes = None):
        session = self.Session()
        try:
            ctx = Context(topic=topic, conversation_id=conversation_id, content=content, embedding=embedding)
            session.add(ctx)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def get_context(self, topic: str = None, conversation_id: str = None) -> List[Dict[str, Any]]:
        session = self.Session()
        try:
            query = session.query(Context)
            if topic:
                query = query.filter(Context.topic == topic)
            if conversation_id:
                query = query.filter(Context.conversation_id == conversation_id)
            results = query.order_by(Context.timestamp.desc()).limit(10).all()
            return [
                {
                    'id': ctx.id,
                    'topic': ctx.topic,
                    'conversation_id': ctx.conversation_id,
                    'content': ctx.content,
                    'timestamp': ctx.timestamp,
                    'embedding': ctx.embedding
                } for ctx in results
            ]
        finally:
            session.close()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contexts (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                conversation_id TEXT,
                user_input TEXT,
                agent_response TEXT,
                timestamp DATETIME,
                response_type TEXT  -- 'user', 'agent', 'system'
            )
        """)
        conn.commit()
        conn.close()

    def save_context(self, topic: str, conversation_id: str, user_input: str = None, 
                    agent_response: str = None, response_type: str = "user"):
        """Save context with proper filtering - NO main model outputs"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO contexts (topic, conversation_id, user_input, agent_response, timestamp, response_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (topic, conversation_id, user_input, agent_response, datetime.now(), response_type))
        conn.commit()
        conn.close()

    def get_filtered_context(self, topic: str = None, conversation_id: str = None, 
                           exclude_main_model: bool = True) -> str:
        """Get context formatted for agents, excluding main model outputs"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT user_input, agent_response, timestamp, response_type 
            FROM contexts 
            WHERE 1=1
        """
        params = []
        if topic:
            query += " AND topic = ?"
            params.append(topic)
        if conversation_id:
            query += " AND conversation_id = ?"
            params.append(conversation_id)
        if exclude_main_model:
            query += " AND response_type != 'main_model'"
        query += " ORDER BY timestamp DESC LIMIT 10"
        results = conn.execute(query, params).fetchall()
        conn.close()
        # Format context for agents
        context_text = "Previous conversation context:\n"
        for row in reversed(results):  # Reverse to show chronological order
            user_input, agent_response, timestamp, response_type = row
            if user_input:
                context_text += f"User: {user_input}\n"
            if agent_response:
                context_text += f"Agent: {agent_response}\n"
            context_text += f"Time: {timestamp}\n---\n"
        return context_text

    def get_last_user_query(self, topic: str = None, conversation_id: str = None) -> str:
        conn = sqlite3.connect(self.db_path)
        query = "SELECT user_input FROM contexts WHERE response_type = 'user'"
        params = []
        if topic:
            query += " AND topic = ?"
            params.append(topic)
        if conversation_id:
            query += " AND conversation_id = ?"
            params.append(conversation_id)
        query += " ORDER BY timestamp DESC LIMIT 1"
        result = conn.execute(query, params).fetchone()
        conn.close()
        return result[0] if result else ""
