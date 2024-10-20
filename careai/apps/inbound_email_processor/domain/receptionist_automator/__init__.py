import datetime
import email
import imaplib
import logging
import os
from email.utils import parsedate_to_datetime

from careai.apps.inbound_email_processor.beans import Config, Email, EmailStatus
from careai.apps.inbound_email_processor.data_store.email.data_store import upsert_email
from careai.apps.inbound_email_processor.domain.document_processor import (
    extract_from_document,
)
from careai.apps.inbound_email_processor.domain.email import format_medical_report
from careai.apps.inbound_email_processor.domain.report_extractor import (
    extract_and_summarize_medical_report,
)

# Email account credentials
email_user = os.getenv("EMAIL_USER")
email_password = os.getenv("EMAIL_PASSWORD")
# from_email_filter = "tech@careaihq.com"


def poll_and_process_message(config: Config):
    """
    Polls the Gmail inbox for new emails from the given email address
    and processes the email content to extract medical reports and
    sends them to the identified doctors.

    The process involves:
        1. Connecting to the Gmail IMAP server
        2. Logging in to your account
        3. Selecting the "inbox" mailbox
        4. Searching for unread emails from the given email address
        5. Fetching the email content for each unread email
        6. Parsing the email content to extract the report_extractor
        7. Saving the report_extractor as a file
        8. Extracting the medical report content from the file
        9. If the report_extractor is a medical report, identifies the doctor
           from the database using the doctor's first and last names
        10. Sends the medical report to the identified doctor if found
        11. Marks the report_extractor as read

    Args:
        config (Config): The configuration object containing the email
            account credentials and database connection details.

    Returns:
        None
    """

    # Connect to the Gmail IMAP server
    mail = imaplib.IMAP4_SSL(config.email_config.imap_endpoint)

    # Login to your account
    mail.login(email_user, email_password)

    # Select the mailbox you want to check (e.g., 'INBOX')
    mail.select("inbox")
    # Search for all unread emails
    # status, messages = mail.search(None, f'(UNSEEN FROM "{config.email_config.from_email_filter}")')

    # Process each report_extractor
    # Global variable to store the last processed time
    global last_processed_time
    if "last_processed_time" not in globals():
        last_processed_time = datetime.datetime.now()

    def get_last_processed_time():
        global last_processed_time
        # Ensure last_processed_time is timezone-aware
        if last_processed_time.tzinfo is None:
            last_processed_time = last_processed_time.replace(
                tzinfo=datetime.timezone.utc
            )
        return last_processed_time

    def save_last_processed_time(timestamp):
        global last_processed_time
        last_processed_time = timestamp

    # Get the timestamp of the last processed email
    current_last_processed_time = get_last_processed_time()

    # Search for emails newer than the last processed email
    date_string = current_last_processed_time.strftime("%d-%b-%Y")
    search_criteria = f'(SINCE "{date_string}")'

    status, messages = mail.search(None, search_criteria)

    if not messages[0]:
        logging.info("No new emails found.")
        return

    email_ids = messages[0].split()

    for email_id in email_ids:
        _, uid_data = mail.fetch(email_id, "(UID)")
        uid = (
            uid_data[0].decode().split()[-1].rstrip(")")
        )  # Extract the UID from the response

        # Fetch the email by ID
        status, msg_data = mail.fetch(email_id, "(RFC822)")

        # Parse the email content
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_date = parsedate_to_datetime(msg["Date"])

                # Ensure both datetimes are timezone-aware before comparison
                current_last_processed_time = get_last_processed_time()
                if email_date.tzinfo is None:
                    email_date = email_date.replace(tzinfo=datetime.timezone.utc)

                # Now compare the timezone-aware datetimes
                if email_date <= current_last_processed_time:
                    continue
                logging.info(f"Processing email ID: {email_id.decode()}, uid: {uid}")

                original_email_subject = msg["subject"]
                original_email_from_address = msg["from"]
                logging.info(f"From: {original_email_from_address}")
                logging.info(f"Subject: {original_email_subject}")

                original_email_text = ""
                for part in msg.walk():
                    if part.get_content_maintype() == "text":
                        original_email_text += part.get_payload()
                    elif part.get_content_disposition() == "attachment":
                        filename = part.get_filename()
                        if filename:
                            attachment_filepath = os.path.join(
                                config.email_config.attachments_dir, filename
                            )
                            with open(attachment_filepath, "wb") as f:
                                f.write(part.get_payload(decode=True))
                            logging.info(f"Saved attachment: {attachment_filepath}")
                            extract_content = extract_from_document(attachment_filepath)
                            print(extract_content)
                            if extract_content:
                                medical_report = extract_and_summarize_medical_report(
                                    attachment_filepath, extract_content
                                )
                                if not medical_report.is_document_medical_report:
                                    logging.warn(
                                        "Looks like report does not contain medical information, skipping it"
                                    )
                                else:
                                    email_content = format_medical_report(
                                        medical_report
                                    )
                                    email_data = Email(
                                        email_id=str(int(uid)),
                                        to_address=config.email_config.doctor_email_address,
                                        email_subject=medical_report.email_subject,
                                        email_content=email_content,
                                        attachments=[attachment_filepath],
                                        status=EmailStatus.PENDING,
                                        original_email_text=original_email_text,
                                        original_email_subject=original_email_subject,
                                        original_email_from_address=original_email_from_address,
                                        doctor_first_name=medical_report.doctor_first_name,
                                        doctor_last_name=medical_report.doctor_last_name,
                                        patient_first_name=medical_report.patient_first_name,
                                        patient_last_name=medical_report.patient_last_name,
                                        report_type=medical_report.report_type,
                                    )
                                    upsert_email(email_data)

                # Update the last processed time
                if email_date > current_last_processed_time:
                    current_last_processed_time = email_date

    # Save the last processed time for the next iteration
    save_last_processed_time(current_last_processed_time)
    # Logout
    mail.logout()
