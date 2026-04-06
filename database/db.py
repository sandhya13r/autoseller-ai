# database/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config

engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# ── Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Create all tables
def init_db():
    from database.models import (
        User, Item, Listing,
        Negotiation, Shipment, Transaction, Notification
    )
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")