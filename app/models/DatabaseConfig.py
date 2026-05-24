from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    db_type: str
    db_name: str
    host: str = ""
    port: str = ""
    username: str = ""
    password: str = ""