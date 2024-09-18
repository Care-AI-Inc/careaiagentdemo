from typing import List, Optional

from pydantic import BaseModel, BaseConfig



class MedicalReport(BaseModel):
    is_document_medical_report: bool
    doctor_first_name: Optional[str] = ""
    doctor_last_name: Optional[str] = ""
    patient_first_name: Optional[str] = ""
    patient_last_name: Optional[str] = ""
    summary: Optional[str] = ""
    email_subject: Optional[str] = ""
    critical_findings: Optional[str] = ""
    recommendations: Optional[str] = ""
    report_date: Optional[str] = ""
    report_type: Optional[str] = ""

class EmailConfig(BaseModel):
    imap_endpoint: str
    smtp_endpoint: str
    smtp_port: int

    from_email_filter: str
    attachments_dir: str

class DBConfig(BaseModel):
    host: str
    port: int
    dbname: str

class Config(BaseModel):
    email_config: EmailConfig
    db_config: DBConfig

from enum import Enum

class EmailStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Email(BaseModel):
    email_id: str
    to_address: Optional[str] = None
    email_subject: Optional[str] = None
    email_content: Optional[str] = None
    attachments: Optional[List[str]] = None
    status: Optional[EmailStatus] = None
