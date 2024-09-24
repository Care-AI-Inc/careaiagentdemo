CREATE TABLE IF NOT EXISTS emails (
    email_id VARCHAR PRIMARY KEY,
    email_content TEXT,
    email_subject TEXT,
    attachments TEXT[],
    to_address VARCHAR,
    status VARCHAR CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    created_date TIMESTAMP
);