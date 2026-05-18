from fastapi import APIRouter, HTTPException
from app.repositories.AIAgentRepository import AIAgentRepository
from app.services.AlAgentServise import AlAgentServise

router = APIRouter()
repo = AIAgentRepository()
AiAgentService = AlAgentServise()

@router.get("/database")
def get_database():
    return repo.get_database_schema()


@router.post("/query")
def call_ai_agent(query: str):
     return AiAgentService.callAlAgent(query)

