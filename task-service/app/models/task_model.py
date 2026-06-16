from sqlalchemy import Column, String, Boolean, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import uuid

DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    assigned_to = Column(String, nullable=False)

    status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    """
    FastAPI calls this function automatically whenever a route needs a DB session.
    The 'yield' makes it a generator — code before yield = setup, after = cleanup.
    This guarantees the session is ALWAYS closed, even if an error happens.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()