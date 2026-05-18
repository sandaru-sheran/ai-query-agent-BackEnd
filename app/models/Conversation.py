from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.core.database import Base
from datetime import datetime
from typing import Annotated, Sequence, TypedDict, List
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50))
    content = Column(Text)

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content
        }

class ConversationAgent(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
