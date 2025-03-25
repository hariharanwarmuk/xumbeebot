import psycopg2
import os
from psycopg2.extras import RealDictCursor
from vector_search import build_kb_index, search_kb
from dotenv import load_dotenv
load_dotenv()


DB_NAME = os.environ.get("DB_NAME", "mydb")
DB_USER = os.environ.get("DB_USER", "myuser")
DB_PASS = os.environ.get("DB_PASS", "mypassword")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
print("DB_NAME", DB_NAME)
print("DB_USER", DB_USER)       

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )

def get_case_info(case_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cases WHERE case_id=%s", (case_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row if row else None

def assign_case_to_agent(case_id, agent_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE cases SET assigned_agent_id=%s WHERE case_id=%s",
        (agent_id, case_id)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_all_kb_entries():
    """
    Retrieve all knowledge base entries.
    Each entry is a dict with keys 'question' and 'answer'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT question, answer FROM knowledge_base ORDER BY kb_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
def search_knowledge_base_vector(question):
    """
    Search the knowledge base using vector search (with fuzzy matching).
    Returns the matching KB entry (question and answer) or None if no match is found.
    """
    kb_entries = get_all_kb_entries()
    if not kb_entries:
        return None
    index, mapping = build_kb_index(kb_entries)
    result, distance = search_kb(question, index, mapping, top_k=1)
    print("Results from search_kb (ventor db):", result, distance)
    return result


def search_faqs(question):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT faq_question, faq_answer
        FROM faqs
        WHERE faq_question ILIKE %s
        LIMIT 1
    """, (f"%{question}%",))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row if row else None

def get_all_faqs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT faq_question, faq_answer FROM faqs ORDER BY faq_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_open_cases():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cases WHERE case_status ILIKE 'Open' ORDER BY case_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def save_chat_message(user_id, case_id, role, text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chat_history (user_id, case_id, message_role, message_text)
        VALUES (%s, %s, %s, %s)
    """, (user_id, case_id, role, text))
    conn.commit()
    cur.close()
    conn.close()

def get_chat_history(user_id, case_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT message_role as role, message_text as content, timestamp
        FROM chat_history
        WHERE user_id = %s AND case_id = %s
        ORDER BY timestamp ASC
    """, (user_id, case_id))
    history = cur.fetchall()
    cur.close()
    conn.close()
    return list(history)

# if __name__ == "__main__":
#     # Test the search_knowledge_base_vector function
#     question = "How to refund?"
#     result = search_knowledge_base_vector(question)
#     if result:
#         print(f"Found answer: {result['answer']}")
#     else:
#         print("No answer found in the knowledge base.")