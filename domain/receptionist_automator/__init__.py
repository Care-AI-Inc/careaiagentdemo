import email
import imaplib
import logging
import os

from beans import Config, EmailStatus
from data_store import get_doctor_data
from data_store.email import upsert_email
from domain.document_processor import extract_from_document
from domain.email import format_medical_report
from domain.report_extractor import extract_and_summarize_medical_report

# Email account credentials
email_user = os.getenv('EMAIL_USER')
email_password = os.getenv('EMAIL_PASSWORD')
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
    mail.select('inbox')
    # Search for all unread emails
    status, messages = mail.search(None, f'(UNSEEN FROM "{config.email_config.from_email_filter}")')

    if not messages:
        return

    # Convert the result to a list of report_extractor IDs
    email_ids = messages[0].split()

    # Process each report_extractor
    for email_id in email_ids:
        # Fetch the report_extractor by ID
        status, msg_data = mail.fetch(email_id, '(RFC822)')

        # Parse the report_extractor content
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_subject = msg['subject']
                email_from = msg['from']
                logging.info(f'From: {email_from}')
                logging.info(f'Subject: {email_subject}')

                for part in msg.walk():
                    # Check if the part is an attachment
                    if part.get_content_disposition() == 'attachment':
                        filename = part.get_filename()
                        if filename:
                            attachment_filepath = os.path.join(config.email_config.attachments_dir, filename)
                            # Save the attachment
                            with open(attachment_filepath, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            logging.info(f'Saved attachment: {attachment_filepath}')
                            extract_content = extract_from_document(attachment_filepath)
                            print(extract_content)
                            if extract_content:
                                medical_report = extract_and_summarize_medical_report(extract_content)
                                if not medical_report.is_document_medical_report:
                                    logging.warn("Looks like report does not contain medical information, skipping it")
                                doctor_data = get_doctor_data()
                                # doctor_ids = normalize_and_find_matching_name_ids(get_doctor_data(),
                                #                                                   medical_report.doctor_first_name,
                                #                                                   medical_report.doctor_last_name)
                                # if not doctor_ids:
                                #     logging.info(
                                #         f"Unable to find doctor from database for extracted doctor {medical_report.doctor_first_name} {medical_report.doctor_last_name}")
                                #     break
                                # if len(doctor_ids) > 1:
                                #     logging.info(
                                #         f"Multiple doctor found for the report, not sure to whom to sent the report {doctor_ids}")
                                #     break
                                # logging.info("Identified doctor id %s for doctor name %s %s", doctor_ids[0],
                                #              medical_report.doctor_first_name, medical_report.doctor_last_name)
                                # overriding doctor name to match with DB to maintain consistency
                                # doctor_info = doctor_data[doctor_ids[0]]
                                # medical_report.doctor_first_name = doctor_info["first_name"]
                                # medical_report.doctor_last_name = doctor_info["last_name"]
                                email_content = format_medical_report(medical_report)
                                upsert_email(str(int(email_id)), config.email_config.doctor_email_address, medical_report.email_subject, email_content, [attachment_filepath], EmailStatus.PENDING)
                                # email_medical_report(config.email_config, doctor_info["email"], medical_report.email_subject,
                                #                      email_content)

        # Mark the report_extractor as read
        mail.store(email_id, '+FLAGS', '\\Seen')

    # Logout
    mail.logout()
