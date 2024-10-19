from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from careai.utils import fetch_config

from .beans import Email, EmailStatus, EmailUpdate
from .data_store.email import fetch_email_by_id, fetch_emails, update_email
from .domain.email import email_medical_report

router = APIRouter()
config = fetch_config()


@router.get("/")
async def get_emails(
    status: Optional[EmailStatus] = None, limit: int = 20, offset: int = 0
):
    return [
        Email(
            email_id=email.email_id,
            email_content=email.email_content,
            email_subject=email.email_subject,
            original_email_subject=email.original_email_subject,
            original_email_from_address=email.original_email_from_address,
            original_email_text=email.original_email_text,
            attachments=email.attachments,
            to_address=email.to_address,
            status=EmailStatus(email.status.value),
        )
        for email in fetch_emails(status, offset, limit)
    ]


@router.patch("/{email_id}")
async def patch_email(email_id: str, email: EmailUpdate):
    update_email(
        email_id,
        email.to_address,
        email.email_subject,
        email.email_content,
        email.attachments,
        email.status,
    )
    return email


@router.get("/{email_id}")
async def get_email_by_id(email_id: str):
    email = fetch_email_by_id(email_id)
    if email:
        return email
    raise HTTPException(status_code=404, detail="Email not found")


@router.post("/{email_id}/accept")
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
    else:
        raise HTTPException(status_code=404, detail="Email not found")


@router.post("/{email_id}/reject")
async def reject_email(email_id: str):
    email = fetch_email_by_id(email_id)
    if email:
        update_email(email_id, status=EmailStatus.REJECTED)
    else:
        raise HTTPException(status_code=404, detail="Email not found")


@router.get("/{email_id}/attachment")
async def get_attachment(email_id: str):
    email = fetch_email_by_id(email_id)
    if email and email.attachments:
        file_path = email.attachments[0]
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=f"{email.email_subject}.pdf",
        )
    raise HTTPException(status_code=404, detail="Attachment not found")
