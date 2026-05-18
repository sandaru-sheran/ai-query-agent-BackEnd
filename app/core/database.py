from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL connection details
MYSQL_URL = "mysql+pymysql://root:1234@localhost:3306/uni"
CONVERSATION_DB_URL = "mysql+pymysql://root:1234@localhost:3306/conversation"

engine = create_engine(MYSQL_URL)
conversation_engine = create_engine(CONVERSATION_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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
