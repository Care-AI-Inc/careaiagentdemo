import os

import yaml
from careai.apps.inbound_email_processor.beans import EmailConfig, Config, DBConfig


def fetch_config() -> Config:
    """Fetches the config file and returns the config object"""
    config_file = os.getenv('CONFIG_FILE')
    
    if not config_file:
        raise ValueError("CONFIG_FILE env variable is not set")

    with open(config_file, 'r') as file:
        config_data = yaml.safe_load(file)
    # Create the config
    email_config = EmailConfig(
        imap_endpoint=config_data['email']['imap_endpoint'],
        smtp_endpoint=config_data['email']['smtp_endpoint'],
        smtp_port=config_data['email']['smtp_port'],
        from_email_filter=config_data['email']['from_email_filter'],
        attachments_dir=config_data['email']['attachments_dir'],
        doctor_email_address=config_data['email']['doctor_email_address']
    )
    db_config = DBConfig(
        host=config_data['db']['host'],
        port=config_data['db']['port'],
        dbname=config_data['db']['dbname']
    )
    config = Config(email_config=email_config, db_config=db_config)
    return config
