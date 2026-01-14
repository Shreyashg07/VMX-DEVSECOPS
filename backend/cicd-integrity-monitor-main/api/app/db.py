import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = os.environ.get("INTEGRITY_DB_PATH", "sqlite:///./integrity.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False} if "sqlite" in DB_PATH else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    from api.app import models
    Base.metadata.create_all(bind=engine)
