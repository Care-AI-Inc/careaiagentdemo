from typing import List, Optional

from pydantic import BaseModel, BaseConfig


class Email(BaseModel):
    subject: str
    body: str
    from_address: str
    to_address: str
    attachments_files: List[str]


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

class Config(BaseModel):
    email_config: EmailConfig
