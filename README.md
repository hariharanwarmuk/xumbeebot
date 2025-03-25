# Customer Service Agentic Chatbot

This project implements an agentic chatbot designed to assist customer service agents in discussing and resolving customer cases. The chatbot leverages OpenAI GPT-4o with function calling, persistent conversation storage in PostgreSQL, and a vector-based knowledge base search (using FAISS and OpenAI embeddings) to provide actionable suggestions and case summaries.

## Features

- **Agent Login & Session Management:**  
  Secure login for customer service agents with persistent sessions.

- **Case Management:**  
  Agents can select an open case to open a dedicated chat window. Each case has its own conversation history stored in PostgreSQL.

- **Persistent Conversation History:**  
  All messages are stored in the database per (user, case) pair. This allows agents to resume previous conversations even after closing the browser.

- **OpenAI Function Calling:**  
  The chatbot uses OpenAI GPT-4o to process messages. It dynamically calls functions such as:
  - `get_case_info`: Fetch case details from the database.
  - `search_knowledge_base_vector`: Perform a fuzzy, vector-based search on the knowledge base.
  - `assign_case_to_agent`: Assign a case to a specific agent.

- **Vector-Based Knowledge Base Search:**  
  Uses FAISS and OpenAI embeddings (via the model `text-embedding-3-small`) to perform fuzzy matching against the knowledge base.

- **Final Answer Refinement:**  
  The final answer is refined using a dedicated LLM call that takes the entire conversation context into account.

## Project Structure

- `bot/`
  - `app.py` - Flask application entry point
  - `db_setup.py` - Database initialization
  - `db_queries.py` - Database operations
  - `openai_client.py` - OpenAI API integration
  - `vector_search.py` - FAISS vector search implementation
  - `templates/` - HTML templates
    - `login.html`
    - `chat.html`
    - `select_case.html`

## Setup

1. Install dependencies:
```bash
pip install -r bot/requirements.txt
```

2. Configure environment variables in .env:
```
DB_NAME=xumbee
DB_USER=postgres
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your_openai_key
FLASK_SECRET_KEY=your_secret_key
```

3. Initialize database:
```bash
python bot/db_setup.py
```

4. Run the application:
```bash
python bot/app.py
```