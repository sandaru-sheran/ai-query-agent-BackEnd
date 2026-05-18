from langchain_core.messages import HumanMessage, AIMessage

from app.repositories.ConversationRepository import ConversationRepository


class ConvasationServise:

    def __init__(self):
        self.repository = ConversationRepository()

    def get_history(self) -> list[dict]:
        raw_messages = self.repository.load_messages() or []
        mapped_history = []
        for msg in raw_messages:
            if isinstance(msg, HumanMessage):
                role = "human"
            elif isinstance(msg, AIMessage):
                role = "ai"
            else:
                continue
            mapped_history.append({
                "role": role,
                "content": msg.content
            })
        return mapped_history