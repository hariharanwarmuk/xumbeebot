import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def create_tables():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()

    # 1) Users table (agents)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(200) NOT NULL
    );
    """)

    # 2) Cases table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id SERIAL PRIMARY KEY,
        case_subject TEXT,
        case_transcript TEXT,
        case_priority TEXT,
        case_status TEXT,
        case_sentiment TEXT,
        assigned_agent_id INT REFERENCES users(user_id)
    );
    """)

    # 3) Knowledge Base table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_base (
        kb_id SERIAL PRIMARY KEY,
        question TEXT UNIQUE,
        answer TEXT
    );
    """)

    # 4) FAQs table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS faqs (
        faq_id SERIAL PRIMARY KEY,
        faq_question TEXT UNIQUE
    );
    """)

    # 5) Chat History
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        chat_id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(user_id),
        case_id INT REFERENCES cases(case_id),
        message_role VARCHAR(20),  -- 'user' or 'assistant'
        message_text TEXT,
        timestamp TIMESTAMP DEFAULT NOW()
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

def insert_initial_data():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()

    # Insert sample users (agents)
    cur.execute("""
    INSERT INTO users (username, password_hash)
    VALUES
        ('agent_john', 'hashed_pw_john'),
        ('agent_jane', 'hashed_pw_jane')
    ON CONFLICT (username) DO NOTHING;
    """)


    # Insert sample knowledge base items
    cur.execute("""
    INSERT INTO knowledge_base (question, answer)
    VALUES
        ('How to troubleshoot error code 404?', 'Check if the URL is correct. If so, restart the router...'),
        ('How to fix battery draining fast?', 'Dim screen brightness, disable background apps...')
    ON CONFLICT DO NOTHING;
    """)

    # Insert sample FAQs
    cur.execute("""
    INSERT INTO faqs (faq_question, faq_answer)
    VALUES
        ('How can I summarize a case?', 'Use the Summarize command to get a short version of the case details.'),
        ('How to assign a case to an agent?', 'Use the command Assign Case with agent name or ID.')
    ON CONFLICT DO NOTHING;
    """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    # create_tables()
    # print("Database tables created successfully.")
    insert_initial_data()
    print("Data inserted successfully.")
    
