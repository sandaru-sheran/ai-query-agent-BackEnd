import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from models import DatabaseConfig
from app.services.DatabaseConnectionManagerServise import DatabaseConnectionManagerServise
load_dotenv()

Base = declarative_base()

# --- 1. Static Conversation DB (Remains Unchanged) ---
CONVERSATION_DB_URL = os.getenv("CONVERSATION_DB_URL")
conversation_engine = create_engine(CONVERSATION_DB_URL)
ConversationSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=conversation_engine)


def get_conversation_db():
    return ConversationSessionLocal()

# --- 2. Dynamic UNI DB (Stateful) ---

# Initialize these as None. They will be populated when you call set_dynamic_db
database_engine = create_engine(os.getenv("UNI_DB_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database_engine)


def set_dynamic_db(config: DatabaseConfig):
    """
    Sets the global database engine.
    It will stay connected to this database until this method is called again.
    """
    global database_engine, SessionLocal

    # Clean up the old engine's connections if one already exists
    if database_engine is not None:
        database_engine.dispose()

    # Create the new engine and session maker
    factory = DatabaseConnectionManagerServise()
    database_engine = factory.get_engine(config)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database_engine)

    print(f"Database switched dynamically to: {config.db_name}")


def get_db():
    """
    Yields a session for the currently active dynamic database.
    """
    if SessionLocal is None:
        raise Exception("Database is not initialized. Please call set_dynamic_db() first.")

    return SessionLocal()
