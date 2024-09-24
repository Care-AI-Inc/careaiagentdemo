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
    'host': 'db',  # or your database host
    'port': '5432'  # default PostgreSQL port
}

# Initialize the database connection
import psycopg2.pool

_connection_pool: Optional[psycopg2.pool.SimpleConnectionPool] = None

def get_connection():
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **db_params)
    return _connection_pool.getconn()

def release_connection(connection):
    if not connection:
        return
    global _connection_pool
    if _connection_pool:
        _connection_pool.putconn(connection)

# Function to insert data into the emails table
def upsert_email(email_id, to_address, email_subject, email_content, attachments, status: EmailStatus):
    conn = get_connection()
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
        release_connection(conn)

def fetch_email_by_id(email_id: str) -> Optional[Email]:
    conn = get_connection()
    cur = None
    try:
        cur = conn.cursor()
        # SQL query to fetch email by id
        query = '''
        SELECT email_id, to_address, email_subject, email_content, attachments, status 
        FROM emails 
        WHERE email_id = %s;
        '''
        cur.execute(query, (email_id,))
        row = cur.fetchone()
        if row:
            return Email(
                email_id=row[0],
                to_address=row[1],
                email_subject=row[2],
                email_content=row[3],
                attachments=row[4],
                status=EmailStatus(row[5])
            )
    except Exception as error:
        print(f"Error fetching email: {error}")
    finally:
        if cur is not None:
            cur.close()
        release_connection(conn)

def fetch_emails(status: Optional[EmailStatus] = None) -> List[Email]:
    conn = get_connection()
    cur = None
    try:
        cur = conn.cursor()
        # SQL query to fetch pending emails sorted by created_date
        query = '''
        SELECT email_id, to_address, email_subject, email_content, attachments, status 
        FROM emails 
        '''
        if status is not None:
            query += ' WHERE status = %s '

        query += ' ORDER BY created_date DESC;'

        cur.execute(query, (status.value,) if status is not None else ())

        # Fetch all results
        rows = cur.fetchall()

        # Convert each row into an Email instance
        emails = [
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

        return emails

    except Exception as error:
        print(f"Error fetching emails: {error}")
        return []

    finally:
        if cur is not None:
            cur.close()
        release_connection(conn)

def update_email(email_id, to_address=None, email_subject=None, email_content=None, attachments=None, status=None):
    conn = get_connection()
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
            update_fields.append("status = %s")
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

    finally:
        if cur is not None:
            cur.close()
        release_connection(conn)
