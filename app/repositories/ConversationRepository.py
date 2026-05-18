from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from sqlalchemy.orm import sessionmaker
from app.models.Conversation import MessageModel
from app.core.database import conversation_engine, Base

class ConversationRepository:
    def __init__(self):
        Base.metadata.create_all(bind=conversation_engine)
        self.SessionLocal = sessionmaker(bind=conversation_engine)

    def save_messages(self, messages: list[BaseMessage]):
        """Saves a collection of new messages using an internal DB session."""
        with self.SessionLocal() as db:
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    role = "human"
                elif isinstance(msg, AIMessage):
                    role = "ai"
                else:
                    continue

                db_message = MessageModel(
                    role=role,
                    content=msg.content
                )
                db.add(db_message)
            db.commit()

    def load_messages(self) -> list[BaseMessage]:
        """Loads historical messages from the internal session ID."""
        with self.SessionLocal() as db:
            db_messages = (
                db.query(MessageModel)
                .order_by(MessageModel.id.asc())
                .all()
            )

            messages = []
            for msg in db_messages:
                if msg.role == "human":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "ai":
                    messages.append(AIMessage(content=msg.content))
                elif msg.role == "system":
                    messages.append(SystemMessage(content=msg.content))
                elif msg.role == "tool":
                    messages.append(ToolMessage(content=msg.content, tool_call_id="hist_fallback"))

            return messages

    def delete_messages(self):
        """Truncates the messages table and resets the auto-increment ID counter."""
        with self.SessionLocal() as db:
            from sqlalchemy import text
            db.execute(text("TRUNCATE TABLE messages;"))
            db.commit()