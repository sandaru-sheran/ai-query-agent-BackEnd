from sqlalchemy.orm import Session
from typing import TypedDict,List
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import Annotated

from app.repositories.AIAgentRepository import AIAgentRepository
from app.repositories.ConversationRepository import ConversationRepository
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from app.models.Conversation import MessageModel, ConversationAgent
class AlAgentServise:
    def __init__(self):
        self.conversationRepo = ConversationRepository()
        self.aiRepo = AIAgentRepository()
        self.messageHistry = self.conversationRepo.load_messages() or []
        self.tools = [
            tool(self.getDatabaseScema),
            tool(self.executeQuery),
            tool(self.validateQuery)
        ]
        self.llm = ChatOpenAI(
                temperature=0.0,
                model_name="qwen2.5-coder-7b-instruct",
                base_url="http://127.0.0.1:1234/v1",
                api_key="lm-studio"
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
        result = self.app.invoke(state)
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
            "1. Do NOT ask the user for confirmation or permission (e.g., never say 'Would you like me to run this?'). Just execute tools immediately.\n"
            "2. If you do not know the layout of the tables, always call 'getDatabaseScema' first.\n"
            "3. MANDATORY VERIFICATION: Before you call 'executeQuery' for any SQL statement, you MUST call 'validateQuery' first to verify it is safe.\n"
            "4. Only call 'executeQuery' if 'validateQuery' returns an APPROVED status.\n"
            "5. Present the data results directly to the user in a clean summary."
        ))

        history = self.conversationRepo.load_messages() or []

        msgs = [system_directive, *history, *state["messages"]]
        response = self.llm.invoke(msgs)

        return {"messages": [response] }

    def repeatAlAgent(self,state : ConversationAgent):
        lastMassege = state["messages"][-1]
        if isinstance(lastMassege, AIMessage) and lastMassege.tool_calls:
            return "continue"
        else:
            return END

    def getDatabaseScema(self) -> dict:
        """Fetch the database schema including table names and their columns."""
        return self.aiRepo.get_database_schema()


    def executeQuery(self, query: str) -> dict:
        """
        Execute a raw SQL query on the database.
        
        Args:
            query: The SQL query string to execute.
        """
        return self.aiRepo.execute_raw_query(query)

    def validateQuery(self, query: str) -> str:
        """
        Validate a SQL query to ensure it doesn't contain forbidden keywords like DROP, DELETE, etc.

        Args:
            query: The SQL query string to validate.
        """
        system_prompt = SystemMessage(content=(
            "You are a strict database security gatekeeper. Analyze the input query. "
            "If the query contains any modifications, deletions, or structural changes "
            "such as DROP, DELETE, UPDATE, INSERT, ALTER, or TRUNCATE, you MUST reject it.\n\n"
            "If rejected, reply exactly with: "
            "'REJECTED: This operation is strictly forbidden. Tell the user that you cannot perform this action.'\n\n"
            "If it is a safe read-only query (like SELECT), reply with: 'APPROVED: Safe to execute.'"
        ))

        human_prompt = HumanMessage(content=f"Query to analyze:\n{query}")

        new_llm = ChatOpenAI(
            temperature=0.0,
            model_name="qwen2.5-coder-7b-instruct",
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio"
        )

        responce = new_llm.invoke([system_prompt, human_prompt])
        return responce.content

    def run_polishing_agent(self, user_query: str, raw_messages: list) -> list[dict]:
        """
        Filters out internal AI tool chatter and polishes the final response.
        """
        raw_final_text = raw_messages[-1].content

        polishing_llm = ChatOpenAI(
            temperature=0.5,  # Higher temperature for better phrasing
            model_name="qwen2.5-coder-7b-instruct",
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio"
        )

        system_directive = SystemMessage(content=(
            "You are a strict Data Formatter and Privacy Filter. Your job is to format raw database output for an end-user.\n\n"
            "CRITICAL RULES:\n"
            "1. NO CHATTER: Do not include ANY introductory or concluding sentences (e.g., NEVER say 'Let's execute that query', 'Here is the data', or 'To get details...'). Start immediately with the formatted data.\n"
            "2. PRIVACY FIREWALL: You MUST silently remove any sensitive data. Never output passwords, bcrypt hashes, security tokens, or disabled flags. Exclude those fields completely.\n"
            "3. ACCURACY: Keep the safe data values perfectly accurate. Do not change names, IDs, or standard emails."
        ))

        human_prompt = HumanMessage(
            content=f"User asked: {user_query}\n\nRaw Data to format:\n{raw_final_text}"
        )

        polished_result = polishing_llm.invoke([system_directive, human_prompt])

        return [
            {"role": "human", "content": user_query},
            {"role": "ai", "content": polished_result.content}
        ]