CREATE TABLE IF NOT EXISTS emails (
    email_id VARCHAR PRIMARY KEY,
    email_content TEXT,
    email_subject TEXT,
    to_address VARCHAR,
    status VARCHAR CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    created_date TIMESTAMP
);

ALTER TABLE IF EXISTS emails
    ADD COLUMN IF NOT EXISTS original_email_subject TEXT,
    ADD COLUMN IF NOT EXISTS original_email_from_address TEXT,
    ADD COLUMN IF NOT EXISTS original_email_text TEXT;