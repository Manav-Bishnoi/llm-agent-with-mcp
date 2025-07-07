from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from typing import List, Dict, Any, Optional
import sqlite3
try:
    from langchain.memory import ConversationBufferMemory
    from langchain_community.chat_message_histories import RedisChatMessageHistory
except ImportError:
    raise ImportError("LangChain is not installed. Please install it with 'pip install langchain langchain_community'.")

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
    """
    Refactored ContextManager to use LangChain's ConversationBufferMemory for per-user memory.
    Deprecated SQL-based context management.
    """
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.user_memories = {}

    def get_memory(self, user_id: str):
        if user_id not in self.user_memories:
            history = RedisChatMessageHistory(
                session_id=user_id,
                url=self.redis_url
            )
            self.user_memories[user_id] = ConversationBufferMemory(
                chat_memory=history,
                return_messages=True
            )
        return self.user_memories[user_id]

    # Deprecated methods (kept for compatibility, but do nothing)
    def save_context(self, *args, **kwargs):
        pass
    def get_context(self, *args, **kwargs):
        return []
    def init_db(self):
        pass
    def get_filtered_context(self, *args, **kwargs):
        return []
    def format_context_for_agent(self, *args, **kwargs):
        return ""
    def get_last_user_query(self, *args, **kwargs):
        return ""
