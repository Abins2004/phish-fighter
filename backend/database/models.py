from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/data/phish_fighter.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ScanLog(Base):
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    score = Column(Float)
    classification = Column(String) # Safe, Suspicious, Phishing
    is_https = Column(Boolean)
    
def init_db():
    # Make sure directory exists
    os.makedirs("backend/data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
