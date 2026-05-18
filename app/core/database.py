import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
# MySQL connection details
UNI_DB_URL = os.getenv("UNI_DB_URL")
CONVERSATION_DB_URL = os.getenv("CONVERSATION_DB_URL")

uni_engine = create_engine(UNI_DB_URL)
conversation_engine = create_engine(CONVERSATION_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=uni_engine)
ConversationSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=conversation_engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_conversation_db():
    db = ConversationSessionLocal()
    try:
        yield db
    finally:
        db.close()
