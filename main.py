import argparse
import logging
import sys
import time

import nest_asyncio

from beans import EmailConfig, Config
from domain.receptionist_automator import poll_and_process_message

SLEEP_BETWEEN_MESSAGE_POLLING = 10

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Set the log message format
    stream=sys.stdout  # Set the output stream to stdout
)

nest_asyncio.apply()

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Process emails for care ai and automate on behalf of receptionist")

    # Add arguments
    parser.add_argument('--imap_endpoint', type=str, required=True, help='IMAP server endpoint')
    parser.add_argument('--smtp_endpoint', type=str, required=True, help='SMTP server endpoint')
    parser.add_argument('--smtp_port', type=int, required=True, help='SMTP server port')
    parser.add_argument('--from_email_filter', type=str, required=True, help='Filter for from email')

    # Parse the arguments
    args = parser.parse_args()

    # Access the arguments
    print(f"IMAP Endpoint: {args.imap_endpoint}")
    print(f"SMTP Endpoint: {args.smtp_endpoint}")
    print(f"SMTP Port: {args.smtp_port}")
    print(f"From Email Filter: {args.from_email_filter}")
    email_config = EmailConfig(
        imap_endpoint=args.imap_endpoint,
        smtp_endpoint=args.smtp_endpoint,
        smtp_port=args.smtp_port,
        from_email_filter=args.from_email_filter
    )
    config = Config(email_config=email_config)


    while True:
        logging.info("Polling for new emails")
        poll_and_process_message(config)
        time.sleep(SLEEP_BETWEEN_MESSAGE_POLLING)
        logging.info("Sleeping before retrying")

if __name__ == "__main__":
    main()
