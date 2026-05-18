# AI Query Agent

An autonomous SQL Data Analytics Assistant that converts natural language questions into safe, executable SQL queries. Built with **FastAPI**, **LangChain**, **LangGraph**, and **SQLAlchemy**.

## 🚀 Features

-   **Natural Language to SQL**: Converts user queries into precise SQL statements.
-   **Autonomous Data Exploration**: Automatically fetches database schema to understand table relationships.
-   **Security Gatekeeper**: Validates every generated query against a strict security policy (prevents `DROP`, `DELETE`, `UPDATE`, etc.).
-   **Response Polishing**: Uses a specialized agent to format raw database results into clean, user-friendly summaries while filtering sensitive data (e.g., passwords, tokens).
-   **Conversation History**: Persists chat history to provide context-aware responses.

## 🛠️ Tech Stack

-   **Backend**: FastAPI
-   **AI Framework**: LangChain, LangGraph
-   **LLM**: Qwen 2.5 Coder 7B (via LM Studio)
-   **Database**: MySQL, SQLAlchemy
-   **Language**: Python 3.10+

## 📁 Project Structure

```text
ai-query-agent/
├── app/
│   ├── controller/      # API Endpoints (queryController.py)
│   ├── core/            # Database configuration and connection
│   ├── models/          # SQLAlchemy and Pydantic models
│   ├── repositories/    # Data access layer (DB schema & AI logic)
│   └── services/        # Business logic (AI Agent State Graph)
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## ⚙️ Setup & Installation

### 1. Prerequisites
-   Python 3.10 or higher
-   MySQL Server
-   [LM Studio](https://lmstudio.ai/) (configured with `qwen2.5-coder-7b-instruct`)

### 2. Database Setup
Create two databases in your MySQL server:
1.  `uni`: The target database for analysis.
2.  `conversation`: To store agent chat history.

Update the connection strings in `app/core/database.py` if necessary:
```python
MYSQL_URL = "mysql+pymysql://root:password@localhost:3306/uni"
CONVERSATION_DB_URL = "mysql+pymysql://root:password@localhost:3306/conversation"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Application
```bash
python main.py
```
The API will be available at `http://localhost:8000`.

## 📡 API Endpoints

### Query the AI Agent
-   **Endpoint**: `POST /api/query`
-   **Query Parameter**: `query` (string)
-   **Example**: `http://localhost:8000/api/query?query=Show me the top 5 students by grade`

### Get Database Schema
-   **Endpoint**: `GET /api/database`

## 🔒 Security
The agent includes a **MANDATORY VERIFICATION** step. Every SQL query generated is analyzed by a "Security Gatekeeper" agent. If the query contains any data-modifying keywords (DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE), it is immediately rejected.
