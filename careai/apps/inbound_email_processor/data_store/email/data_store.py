from typing import Optional, List
import datetime

from careai.apps.inbound_email_processor.beans import EmailStatus, Email
from careai.apps.inbound_email_processor.data_store.email.model import (
    EmailModel,
    EmailModelStatus,
    SessionLocal,
)


# Function to insert data into the emails table
def upsert_email(email: Email):
    try:
        with SessionLocal() as session:
            session.merge(
                EmailModel(
                    email_id=email.email_id,
                    email_content=email.email_content,
                    email_subject=email.email_subject,
                    original_email_subject=email.original_email_subject,
                    original_email_from_address=email.original_email_from_address,
                    original_email_text=email.original_email_text,
                    attachments=email.attachments,
                    to_address=email.to_address,
                    status=EmailModelStatus(email.status.value),
                    created_date=datetime.datetime.now(),
                    doctor_first_name=email.doctor_first_name,
                    doctor_last_name=email.doctor_last_name,
                    patient_first_name=email.patient_first_name,
                    patient_last_name=email.patient_last_name,
                    report_type=email.report_type,
                )
            )
            session.commit()
            print("Email inserted successfully")
    except Exception as error:
        print(f"Error inserting email: {error}")


def fetch_email_by_id(email_id: str) -> Optional[Email]:
    try:
        with SessionLocal() as session:
            email_model = session.query(EmailModel).filter_by(email_id=email_id).first()
            if email_model:
                return Email(
                    email_id=email_model.email_id,
                    to_address=email_model.to_address,
                    email_subject=email_model.email_subject,
                    email_content=email_model.email_content,
                    original_email_subject=email_model.original_email_subject,
                    original_email_from_address=email_model.original_email_from_address,
                    original_email_text=email_model.original_email_text,
                    attachments=email_model.attachments,
                    status=EmailStatus(email_model.status.value),
                    doctor_first_name=email_model.doctor_first_name,
                    doctor_last_name=email_model.doctor_last_name,
                    patient_first_name=email_model.patient_first_name,
                    patient_last_name=email_model.patient_last_name,
                    report_type=email_model.report_type,
                )
    except Exception as error:
        print(f"Error fetching email: {error}")


def fetch_emails(
    status: Optional[EmailStatus] = None, offset: int = 0, limit: int = 20
) -> List[EmailModel]:
    try:
        with SessionLocal() as session:
            query = session.query(EmailModel)
            if status is not None:
                query = query.filter_by(status=status.value)

            query = query.order_by(EmailModel.created_date.desc())
            query = query.offset(offset).limit(limit)
            print("Query is:")
            print(query.statement.compile(compile_kwargs={"literal_binds": True}))
            print("query is " + str(query))
            return query.all()
    except Exception as error:
        print(f"Error fetching emails: {error}")
        return []


def update_email(
    email_id,
    to_address=None,
    email_subject=None,
    email_content=None,
    attachments=None,
    status=None,
):
    try:
        with SessionLocal() as session:
            email_model = session.query(EmailModel).filter_by(email_id=email_id).first()
            if email_model is None:
                print(f"Email with id {email_id} does not exist")
                return

            if to_address is not None:
                email_model.to_address = to_address
            if email_subject is not None:
                email_model.email_subject = email_subject
            if email_content is not None:
                email_model.email_content = email_content
            if attachments is not None:
                email_model.attachments = attachments
            if status is not None:
                email_model.status = status.value

            session.commit()
            print("Email updated successfully")
    except Exception as error:
        print(f"Error updating email: {error}")
