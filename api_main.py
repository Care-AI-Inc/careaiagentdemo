from typing import Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from beans import EmailStatus, EmailUpdate, Email
from data_store.email import fetch_emails, update_email, fetch_email_by_id
from domain.email import email_medical_report
from utils import fetch_config

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
async def get_emails(status: Optional[EmailStatus] = None, limit: int = 20, offset: int = 0):
    return [Email(
        email_id=email.email_id,
        email_content=email.email_content,
        email_subject=email.email_subject,
        original_email_subject=email.original_email_subject,
        original_email_from_address=email.original_email_from_address,
        original_email_text=email.original_email_text,
        attachments=email.attachments,
        to_address=email.to_address,
        status=EmailStatus(email.status.value)
    ) for email in fetch_emails(status, offset, limit)]


@app.patch("/emails/{email_id}")
async def patch_email(email_id: str, email: EmailUpdate):
    update_email(email_id, email.to_address, email.email_subject, email.email_content, email.attachments, email.status)
    return email
@app.get("/emails/{email_id}")
async def get_email_by_id(email_id: str):
    email = fetch_email_by_id(email_id)
    if email:
        return email
    return JSONResponse(status_code=404, content={"message": "Email not found"})

@app.post("/emails/{email_id}/accept")
async def send_email(email_id: str):
    email = fetch_email_by_id(email_id)
    if email:
        email_medical_report(
            email_config=config.email_config,
            to_address=email.to_address,
            subject=email.email_subject,
            body=email.email_content,
            attachment=email.attachments[0] if email.attachments else None,
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