from sqlalchemy import create_engine
from models import DatabaseConfig


class DatabaseConnectionManagerServise:
    def get_engine(self, config: DatabaseConfig):
        if config.db_type == "sqlite":
            db_url = f"sqlite:///{config.db_name}"

        elif config.db_type == "postgresql":
            db_url = f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.db_name}"

        elif config.db_type == "mysql":
            db_url = f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.db_name}"

        elif config.db_type == "oracle":
            db_url = f"oracle+oracledb://{config.username}:{config.password}@{config.host}:{config.port}/{config.db_name}"

        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")

        return create_engine(db_url)