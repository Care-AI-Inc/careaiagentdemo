import argparse
import logging
import sys
import time

import nest_asyncio
import yaml

from apps.inbound_email_processor.beans import EmailConfig, Config
from apps.inbound_email_processor.domain.receptionist_automator import poll_and_process_message
from utils import fetch_config

SLEEP_BETWEEN_MESSAGE_POLLING = 10

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Set the log message format
    stream=sys.stdout  # Set the output stream to stdout
)

nest_asyncio.apply()


def main():
    # Read the yaml file
    config = fetch_config()

    while True:
        logging.info("Polling for new emails")
        poll_and_process_message(config)
        time.sleep(SLEEP_BETWEEN_MESSAGE_POLLING)
        logging.info("Sleeping before retrying")


if __name__ == "__main__":
    main()
