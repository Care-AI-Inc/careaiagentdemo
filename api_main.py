import argparse

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from beans import Email, EmailStatus
from data_store.email import fetch_pending_emails, update_email, fetch_email_by_id
from domain.email import email_medical_report
from utils import fetch_config
from fastapi.responses import FileResponse
app = FastAPI()

# Read the yaml file
config = fetch_config()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/emails")
async def get_emails():
    return fetch_pending_emails()


@app.patch("/emails/{email_id}")
async def patch_email(email_id: str, to_address: str = None, email_subject: str = None, email_content: str = None):
    update_email(email_id, to_address, email_subject, email_content, None, None)
    email = Email(email_id=email_id, to_address=to_address, email_subject=email_subject,
                  email_content=email_content, attachments=[], status=None)
    return email


@app.post("/emails/{email_id}/accept")
async def send_email(email_id: str):
    email = fetch_email_by_id(email_id)
    if email:
        email_medical_report(
            email_config=config.email_config,
            to_address=email.to_address,
            subject=email.email_subject,
            body=email.email_content
        )
        update_email(email_id, status=EmailStatus.APPROVED)

@app.post("/emails/{email_id}/reject")
async def reject_email(email_id: str):
    update_email(email_id, status=EmailStatus.REJECTED)

@app.get("/emails/{email_id}/attachment")
async def get_attachment(email_id: str):
    email = fetch_email_by_id(email_id)
    if email and email.attachments:
        file_path = email.attachments[0]
        return FileResponse(file_path, media_type="application/pdf", filename=f"{email.email_subject}.pdf")