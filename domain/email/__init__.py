import os
import smtplib
import traceback
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import beans

email_user = os.getenv('EMAIL_USER')
email_password = os.getenv('EMAIL_PASSWORD')

MEDICAL_REPORT_BODY = """
Hello Dr. {doctor_first_name} {doctor_last_name}, <br/><br/>

Please find below the summary of the {report_type} for {patient_first_name} {patient_last_name}.<br/><br/>

<b>Report date</b>: {report_date}<br/>

<p>
<b>Critical Findings:</b>  <br/>
{critical_findings}</p>

<p>
<b>Summary:</b><br/>  
{summary}</p>

<p>
<b>Recommendations:</b><br/>  
{recommendations}</p>

<i>This email has been automatically generated by the Care AI System.</i>
"""

def format_medical_report( report: beans.MedicalReport) -> str:
    html_content = MEDICAL_REPORT_BODY.format(**report.model_dump())
    return html_content

def email_medical_report(email_config: beans.EmailConfig, to_address: str, subject: str, body: str, attachment: Optional[str]):
    # Email details
    to_email = to_address
    subject =subject

    # Create the HTML content
    html_content = body

    # Create message
    message = MIMEMultipart()
    message['From'] = email_user
    message['To'] = to_email
    message['Subject'] = subject

    # Attach the HTML content
    message.attach(MIMEText(html_content, 'html'))

    # Attach the file if provided
    if attachment:
        with open(attachment, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(attachment)
        attachment = MIMEApplication(file_data, Name=file_name)
        attachment['Content-Disposition'] = f'attachment; filename="{file_name}"'
        message.attach(attachment)

    # Send the email
    try:
        with smtplib.SMTP(email_config.smtp_endpoint, email_config.smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(email_user, email_password)
            server.sendmail(email_user, to_email, message.as_string())
        print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')
        print(traceback.format_exc())

