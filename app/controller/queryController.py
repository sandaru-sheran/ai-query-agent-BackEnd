from fastapi import APIRouter, HTTPException
from app.repositories.AIAgentRepository import AIAgentRepository
from app.services.AlAgentServise import AlAgentServise
from app.services.ConvasationServise import ConvasationServise
from core import Database
from app.models.DatabaseConfig import DatabaseConfig

router = APIRouter()
repo = AIAgentRepository()
AiAgentService = AlAgentServise()
ConvasationService = ConvasationServise()
databse = Database

@router.get("/database")
def get_database():
    return repo.get_database_schema()

@router.get("/history")
def get_history():
    return ConvasationService.get_history()

@router.delete("/history")
def delete_history():
    ConvasationService.delete_history()

@router.post("/query")
def call_ai_agent(query: str):
     return AiAgentService.callAlAgent(query)[1]

@router.post("/change_database")
def change_database(database_config: DatabaseConfig):
    databse.set_dynamic_db(database_config)
    return "Database changed successfully"


