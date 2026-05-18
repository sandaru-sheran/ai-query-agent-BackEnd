# Full-Stack AI Text-to-SQL Application

## Project Overview
This project is a full-stack AI application that allows users to ask natural language questions about a database and receive answers generated from SQL queries. It is built as part of the CustomMinds Internship Assignment. 

The system utilizes an AI agent workflow to understand the database schema, generate a SQL query, validate the query for safety (blocking destructive commands), execute the query against a MySQL database, and format the results into a clean, human-readable response while stripping sensitive data.

## Tech Stack
* **Frontend:** React (Vite)
* **Backend:** FastAPI (Python)
* **AI Orchestration:** LangGraph & LangChain
* **LLM Engine:** Local models running via LM Studio (Qwen 2.5 Coder)
* **Database:** MySQL with SQLAlchemy ORM

## Architecture Explanation
The application follows a graph-based AI workflow using **LangGraph**:
1.  **Input:** The user submits a natural language question via the React frontend.
2.  **Schema Retrieval:** The AI Agent is strictly blind to the database at the start. If required, it uses the `getDatabaseScema` tool to fetch the current MySQL tables and columns.
3.  **SQL Generation & Validation:** The agent generates a SQL query. Before execution, a mandatory **Security Gatekeeper** (`validateQuery`) checks the SQL. If it contains data-modifying commands (e.g., `DROP`, `DELETE`, `UPDATE`), it is rejected.
4.  **Execution:** If approved, the read-only query is executed against the database via the `executeQuery` tool.
5.  **Polishing:** The raw JSON output from the database is passed to a secondary "Polishing Agent," which formats the data into a conversational response and redacts sensitive information like passwords.
6.  **Output:** The final response is saved to a `conversation` database for chat history and returned to the frontend.

## Setup Instructions

### 1. Prerequisites
* Python 3.10+
* Node.js (v18+)
* MySQL Server
* [LM Studio](https://lmstudio.ai/) running locally on port `1234`.

### 2. Initialize the Database
1. Open your MySQL client (e.g., MySQL Workbench).
2. Run the `app/core/schema.sql` script to create the `ecommerce` and `conversation` databases and their tables.
3. Run the `app/core/seed.sql` script to populate the `ecommerce` database with sample data.

### 3. Backend Setup
1. Navigate to the `backend` directory.
2. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and update your MySQL credentials:
   ```env
   MYSQL_URL="mysql+pymysql://<username>:<password>@localhost:3306/ecommerce"
   CONVERSATION_DB_URL="mysql+pymysql://<username>:<password>@localhost:3306/conversation"
   LLM_BASE_URL="http://127.0.0.1:1234/v1"
   LLM_API_KEY="lm-studio"
   ```
4. Start the FastAPI server:
   ```bash
   python main.py
   ```
   The API will be available at http://localhost:8000.

### 4. Frontend Setup
1. Navigate to the frontend directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the frontend directory:
   ```env
   VITE_API_URL="http://localhost:8000/api"
   ```
4. Start the Vite development server:
   ```bash
   npm run dev
   ```

## Example Questions to Test
The application is currently connected to an E-commerce sample database. Try asking the following baseline questions:
* "Show me a list of all products in the Electronics category."
* "What is the total value of all orders placed so far?"
* "Show me the top customers by order value."
* *Security Test:* "Delete all users from the customers table." (This should be safely blocked by the Security Gatekeeper).

**Model Capability Tests (Prompt Engineering)**
Depending on the size of the LLM loaded in LM Studio, try these prompts to test the agent's ability to autonomously explore the database schema:
* **For 7B Models (Testing Explicit Instruction Adherence):**
  > *"First, call 'getDatabaseScema' to see our layout. Based strictly on the actual tables and columns you find, list 5 specific, real-world analytical questions you can answer for me right now. For each problem, briefly tell me which tables you would join to get the answer."*
* **For 14B+ Models (Testing Autonomous Reasoning & Tool Use):**
  > *"Hey! What are 5 examples of specific questions or data problems you can solve for me using this database?"*

## AI Tool Usage
**AI tools used:** Gemini Pro, JetBrains AI (Junie)

**What AI helped with:** Scaffolding the React frontend components, generating the baseline database schema, and creating the mock seed data. 

**What I personally implemented or modified:** I manually designed and implemented 90% of the LangGraph architecture and the `AIAgentService` logic. Because I spent over 30 hours closely developing, debugging, and refining this project, the rest of the codebase is a seamless blend of my manual coding and AI generation, making it difficult to separate the two line-by-line. 

**Parts I fully understand and can explain:** I fully understand the custom LangGraph routing logic, state management, the SQL security gatekeeper, and the full end-to-end communication flow from the frontend to the database execution.

## Known Limitations
* **Model Constraints (Hallucinations):** Smaller, low-power models (like 7B) exhibit a higher tendency to hallucinate table names or generate inconsistent data if the system prompt's "Blindness Rule" is ignored. This is mitigated by using stronger instruction-tuned models.
* **Architectural Blindspots:** AI tools lacked the high-level context necessary to build a complex backend state machine, requiring manual implementation for all core routing and logic.
* **Hardware Speed:** The application currently relies entirely on a local LLM, which inherently processes requests slower than cloud-based APIs like OpenAI or Anthropic.

## Future Improvements
* **Advanced Data Visualization:** Since users primarily care about fast, actionable results, I plan to integrate a charting library (like Recharts) on the frontend. If the AI detects an aggregation query (e.g., "Top 5 products by revenue"), it will automatically render a bar or pie chart alongside the data table.
* **Dockerization:** Add a `docker-compose.yml` file to spin up the React app, FastAPI backend, and MySQL database simultaneously for a seamless developer setup experience.
* **Voice Input Integration:** Allow users to speak their questions directly into the web interface, making the AI agent feel even more accessible and frictionless.
