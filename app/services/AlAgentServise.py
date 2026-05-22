import os

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from app.repositories.AIAgentRepository import AIAgentRepository
from app.repositories.ConversationRepository import ConversationRepository
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from app.models.Conversation import MessageModel, ConversationAgent

load_dotenv()

class AlAgentServise:
    def __init__(self):
        self.conversationRepo = ConversationRepository()
        self.aiRepo = AIAgentRepository()
        self.messageHistory = self.conversationRepo.load_messages() or []
        self.tools = [
            tool(self.getDatabaseSchema),
            tool(self.executeQuery),
            tool(self.validateQuery)
        ]
        self.llm = ChatOpenAI(
                temperature=os.getenv("AGENT_TEMPERATURE"),
                model_name=os.getenv("AGENT_MODEL_NAME"),
                base_url=os.getenv("LLM_BASE_URL"),
                api_key=os.getenv("LLM_API_KEY")
            ).bind_tools(self.tools)

        self.tool_node = ToolNode(tools=self.tools)
        self.graph = StateGraph(ConversationAgent)
        self.graph.add_node("start", self.startAlAgent)
        self.graph.add_node("tool", self.tool_node)
        self.graph.add_edge(START,"start")
        self.graph.add_edge("tool", "start")
        self.graph.add_conditional_edges("start",self.repeatAlAgent,{
                                            "continue": "tool",
                                            END : END,
                                        })
        self.app = self.graph.compile()

    def callAlAgent(self, query: str) -> list[dict]:
        state = {"messages":self.conversationRepo.load_messages() or []}
        state["messages"].append(HumanMessage(content=query))
        try:
            result = self.app.invoke(state)
        except Exception as e:
            print(f"Graph Execution Error: {e}")
            result = {"messages": [
                AIMessage(content=f"SYSTEM_ERROR: The agent encountered a fatal error and stopped. Details: {str(e)}")]}

        print(result)
        clean_chat = self.run_polishing_agent(query, result["messages"])

        self.conversationRepo.save_messages([
            HumanMessage(content=clean_chat[0]["content"]),
            AIMessage(content=clean_chat[1]["content"])
        ])

        return clean_chat

    def startAlAgent(self, state :ConversationAgent) -> ConversationAgent:
        system_directive = SystemMessage(content=(
            "You are an automated, autonomous SQL Data Analytics Assistant.\n"
            "Your job is to answer user data requests by exploring the database.\n\n"
            "CRITICAL RULES:\n"
            "1. FRESH EVALUATION: Focus entirely on the latest user request. Do NOT reuse, copy, or rely on mock structures, tables, or outputs from the chat history. Treat every new query with a clean slate.\n\n"
            "2. THE BLINDNESS RULE (STRICT SCHEMA INTELLIGENCE): You currently have ZERO knowledge of the database structure. Any tables you assume exist (like 'customers', 'sales', or 'employees') are hallucinations. If the user asks what you can do, asks for examples, or uses words like 'database' or 'schema', you MUST immediately call 'getDatabaseScema' before writing a single word. Never guess the table names.\n\n"
            "3. HANDLING NOT FOUND: If the requested data, table, or column cannot be found anywhere in the database schema, do NOT attempt to generate or execute a query. Instead, respond immediately and cleanly to the user explaining that this information is not available in the current system.\n\n"
            "4. NO CHATTER FOR PERMISSION: Do NOT ask the user for confirmation or permission (e.g., never say 'Would you like me to run this?'). Just execute tools immediately.\n\n"
            "5. MANDATORY VERIFICATION: Before you call 'executeQuery' for any SQL statement, you MUST call 'validateQuery' first to verify it is safe. Only call 'executeQuery' if 'validateQuery' returns an APPROVED status.\n\n"
            "6. EMPTY RESULTS LOGIC: Present the data results directly to the user in a clean summary. If a validated query runs successfully but returns an empty result ([]), state clearly that no matching records were found."
            "7. EXPOSE THE SQL: In your final answer to the user, you MUST include the exact SQL query you executed to retrieve the data. Always place this SQL query at the very end of your response, wrapped in a standard markdown SQL block (```sql ... ```)."
        ))
        history = self.conversationRepo.load_messages() or []

        msgs = [system_directive, *history, *state["messages"]]
        try:
            response = self.llm.invoke(msgs)
            return {"messages": [response]}

        except Exception as e:
            print(f"LLM Invocation Error: {e}")
            error_message = AIMessage(
                content=f"Sorry, I am currently unavailable due to a system or connection error. (Details: {str(e)})")

        return {"messages": [error_message] }

    def repeatAlAgent(self,state : ConversationAgent):
        lastMassege = state["messages"][-1]
        if isinstance(lastMassege, AIMessage) and lastMassege.tool_calls:
            return "continue"
        else:
            return END

    def getDatabaseSchema(self) -> dict | str:
        """
        Fetch the database schema including table names and their column details.

        Returns:
            dict: A dictionary mapping the schema ({"database": [...]}) on success.
            str: An error string prefixed with 'DATABASE_ERROR:' or 'SYSTEM_ERROR:'
                 if the database connection or execution fails, allowing the AI agent
                 to handle the failure gracefully.
        """
        return self.aiRepo.get_database_schema()

    def executeQuery(self, query: str) -> list | str:
        """
        Execute a raw SQL SELECT query on the database.

        Args:
            query (str): The raw SQL query string to execute.

        Returns:
            list: A list of dictionaries containing the fetched rows.
            str: An error string prefixed with 'DATABASE_ERROR:' if the query fails.
        """
        return self.aiRepo.execute_raw_query(query)

    def validateQuery(self, query: str) -> str:
        """
        Validate a SQL query to ensure it doesn't contain destructive commands. Returns an approval status. IMPORTANT: If the query is approved, you MUST subsequently call executeQuery to retrieve the actual data..

        Args:
            query: The SQL query string to validate.
        """
        system_prompt = SystemMessage(content=(
            "You are a strict database security gatekeeper. Analyze the input query. "

            "CRITICAL RULE: If the input is a conversational greeting, a clarification question, "
            "or general text (e.g., 'hi', 'hello', 'how are you'), you MUST approve it. "
            "Reply exactly with: 'APPROVED: Conversational.'\n\n"

            "If the query contains any database modifications, deletions, or structural changes "
            "such as DROP, DELETE, UPDATE, INSERT, ALTER, or TRUNCATE, you MUST reject it. "
            "Reply exactly with: 'REJECTED: This operation is strictly forbidden. Tell the user that you cannot perform this action.'\n\n"

            "If it is a safe read-only query (like SELECT), reply with: 'APPROVED: Safe to execute.'"
        ))
        human_prompt = HumanMessage(content=f"Query to analyze:\n{query}")

        try:
            new_llm = ChatOpenAI(
                temperature=float(os.getenv("VALIDATION_TEMPERATURE", 0.0)),
                model_name=os.getenv("VALIDATION_MODEL_NAME"),
                base_url=os.getenv("LLM_BASE_URL"),
                api_key=os.getenv("LLM_API_KEY")
            )
            response = new_llm.invoke([system_prompt, human_prompt])
            return response.content
        except Exception as e:
            print(f"Validation Agent Error: {e}")
            return f"REJECTED: The security validation service is temporarily unavailable. Cannot execute query. (Details: {str(e)})"

    def run_polishing_agent(self, user_query: str, raw_messages: list) -> list[dict]:
        """
        Filters out internal AI tool chatter and polishes the final response.
        """
        raw_final_text = raw_messages[-1].content

        try:
            polishing_llm = ChatOpenAI(
                temperature=float(os.getenv("POLISH_TEMPERATURE", 0.7)),  # Float cast for safety
                model_name=os.getenv("POLISH_MODEL_NAME"),
                base_url=os.getenv("LLM_BASE_URL"),
                api_key=os.getenv("LLM_API_KEY")
            )

            system_directive = SystemMessage(content=(
                "You are a strict Data Formatter and Privacy Filter. Your job is to format raw database output for an end-user.\n\n"
                "CRITICAL RULES:\n"
                "0. BYPASS CLAUSE: If the raw data input is already conversational text, an explanation, a summary of the database schema, or a friendly message (e.g., descriptions of tables, structural summaries, or regular answers), you MUST output it exactly as it is. Do NOT strip it, do NOT convert it into SQL, and do NOT change a single word. (EXCEPTION: If the text is a system error, follow Rule 4 instead).\n\n"
                "1. NO CHATTER FOR RAW DATA: If the input consists of raw database rows/JSON, do not include ANY introductory or concluding sentences. Start immediately with the formatted data.\n\n"
                "2. PRIVACY FIREWALL: You MUST silently remove password fields. Never output raw passwords or bcrypt hashes. Exclude those fields completely. All other fields (including names, roles, registration numbers, and status flags) are safe to display.\n\n"
                "3. ACCURACY: Keep the safe data values perfectly accurate. Do not change names, IDs, or standard emails.\n\n"
                "4. ERROR TRANSLATION (PRIORITY ORDER): If the input contains a raw technical error, a traceback, or a string starting with 'DATABASE_ERROR:' or 'SYSTEM_ERROR:', you MUST completely hide all technical code and stack traces. Instead, dynamically craft a polite, user-friendly explanation based on the exception using this priority:\n"
                "   - PRIORITY 1 (AI/System Issues): If the error involves LLMs, API, validation, timeouts, or is a 'SYSTEM_ERROR', explain to the user that the AI agent is currently unavailable or experiencing technical difficulties.\n"
                "   - PRIORITY 2 (Database Issues): If the error is strictly a 'DATABASE_ERROR', explain to the user that there is an issue accessing the database or retrieving the requested information."
                "5. PRESERVE SQL BLOCKS: If the input data includes a markdown SQL code block (```sql ... ```) generated by the previous agent, you MUST keep it exactly as it is. Always append this SQL block at the very end of your final formatted response."
            ))

            human_prompt = HumanMessage(
                content=f"User asked: {user_query}\n\nRaw Data to format:\n{raw_final_text}"
            )

            polished_result = polishing_llm.invoke([system_directive, human_prompt])
            final_content = polished_result.content

        except Exception as e:
            print(f"Polishing Agent Error: {e}")
            final_content = f"An error occurred while formatting the final response. Data cannot be securely displayed at this time. (Details: {str(e)})"

        return [
            {"role": "human", "content": user_query},
            {"role": "ai", "content": final_content}
        ]