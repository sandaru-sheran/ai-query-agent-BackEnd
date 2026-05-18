from fastapi import APIRouter, HTTPException
from app.repositories.AIAgentRepository import AIAgentRepository
from app.services.AlAgentServise import AlAgentServise
from app.services.ConvasationServise import ConvasationServise

router = APIRouter()
repo = AIAgentRepository()
AiAgentService = AlAgentServise()
ConvasationService = ConvasationServise()

@router.get("/database")
def get_database():
    return repo.get_database_schema()

@router.get("/history")
def get_history():
    return ConvasationService.get_history()

@router.post("/query")
def call_ai_agent(query: str):
     return AiAgentService.callAlAgent(query)[1]

