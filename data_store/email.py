import os
from typing import Optional, List

import psycopg2
import datetime

from beans import EmailStatus, Email

# Define your database connection parameters
db_params = {
    'dbname': 'careai',
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': 'localhost',  # or your database host
    'port': '5432'  # default PostgreSQL port
}

# Initialize the database connection
try:
    conn = psycopg2.connect(**db_params)
    print("Database connection established")
except Exception as error:
    print(f"Error connecting to the database: {error}")
    conn = None


# Function to insert data into the emails table
def upsert_email(email_id, to_address, email_subject, email_content, attachments, status: EmailStatus):
    cur = None
    try:
        cur = conn.cursor()

        # SQL query to insert data
        upsert_query = '''
                INSERT INTO emails (email_id, email_content, email_subject, attachments, to_address, status, created_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email_id) 
                DO UPDATE SET 
                    email_content = EXCLUDED.email_content,
                    email_subject = EXCLUDED.email_subject,
                    attachments = EXCLUDED.attachments,
                    to_address = EXCLUDED.to_address,
                    status = EXCLUDED.status,
                    created_date = EXCLUDED.created_date;
                '''

        # Execute the query with provided data
        cur.execute(upsert_query, (
        email_id, email_content, email_subject, attachments, to_address, status.value, datetime.datetime.now()))

        # Commit the transaction
        conn.commit()

        print("Email inserted successfully")
    except Exception as error:
        print(f"Error inserting email: {error}")
    finally:
        # Close the cursor if it was initialized
        if cur is not None:
            cur.close()


def fetch_pending_emails() -> List[Email]:
    cur = None
    try:
        cur = conn.cursor()
        # SQL query to fetch pending emails sorted by created_date
        query = '''
        SELECT email_id, to_address, email_subject, email_content, attachments, status 
        FROM emails 
        WHERE status = %s 
        ORDER BY created_date;
        '''

        cur.execute(query, (EmailStatus.PENDING.value,))

        # Fetch all results
        rows = cur.fetchall()

        # Convert each row into an Email instance
        pending_emails = [
            Email(
                email_id=row[0],
                to_address=row[1],
                email_subject=row[2],
                email_content=row[3],
                attachments=row[4],  # Assuming this is stored as a list in PostgreSQL
                status=EmailStatus(row[5])
            )
            for row in rows
        ]

        return pending_emails

    except Exception as error:
        print(f"Error fetching pending emails: {error}")
        return []

    finally:
        if cur is not None:
            cur.close()

def update_email(email_id, to_address=None, email_subject=None, email_content=None, attachments=None, status=None):
    if conn is None:
        print("No database connection available")
        return

    cur = None
    try:
        cur = conn.cursor()

        # Build the update query dynamically based on non-None parameters
        update_fields = []
        values = []

        if to_address is not None:
            update_fields.append("to_address = %s")
            values.append(to_address)

        if email_subject is not None:
            update_fields.append("email_subject = %s")
            values.append(email_subject)

        if email_content is not None:
            update_fields.append("email_content = %s")
            values.append(email_content)

        if attachments is not None:
            update_fields.append("attachments = %s")
            values.append(attachments)

        if status is not None:
            update_fields.append("status = %s::email_status")
            values.append(status.value)

        # Ensure there's something to update
        if not update_fields:
            print("No fields to update")
            return

        # Add email_id for WHERE clause
        values.append(email_id)

        # Construct the SQL query
        query = f"UPDATE emails SET {', '.join(update_fields)} WHERE email_id = %s"

        # Execute the query with provided data
        cur.execute(query, tuple(values))

        # Commit the transaction
        conn.commit()

        print("Email updated successfully")

    except Exception as error:
        print(f"Error updating email: {error}")

    finally:
        if cur is not None:
            cur.close()
