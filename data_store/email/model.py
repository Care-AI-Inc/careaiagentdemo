from sqlalchemy import create_engine, Column, String, DateTime, Enum, LargeBinary, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import datetime
from enum import Enum as PyEnum

Base = declarative_base()

class EmailModelStatus(PyEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class EmailModel(Base):
    __tablename__ = 'emails'

    email_id = Column(String, primary_key=True)
    email_content = Column(String)
    email_subject = Column(String)
    original_email_subject = Column(String)
    original_email_from_address = Column(String)
    original_email_text = Column(String)
    attachments = Column(ARRAY(String))
    to_address = Column(String)
    status = Column(Enum(EmailModelStatus))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    report_type = Column(String)
    doctor_first_name = Column(String)
    doctor_last_name = Column(String)
    patient_first_name = Column(String)
    patient_last_name = Column(String)

# Database connection setup
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@db:5432/careai"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)
