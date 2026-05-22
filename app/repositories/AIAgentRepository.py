from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import uni_engine


class AIAgentRepository:
    def __init__(self):
        self.engine = uni_engine

    def get_database_schema(self):
        database_map = []

        try:
            with self.engine.connect() as connection:
                query_tables = text("SHOW TABLES")
                tables_result = connection.execute(query_tables)

                table_names = [row[0] for row in tables_result]

                for table in table_names:
                    query_desc = text(f"DESCRIBE {table}")
                    desc_result = connection.execute(query_desc)

                    columns_info = [dict(row._mapping) for row in desc_result]

                    database_map.append({
                        "table_name": table,
                        "schema": columns_info
                    })

            return {"database": database_map}

        except SQLAlchemyError as e:
            # Catches database-specific errors (connection drops, timeout, syntax)
            return f"DATABASE_ERROR: Failed to retrieve schema. Details: {str(e)}"

        except Exception as e:
            # Catches any other unexpected Python errors
            return f"SYSTEM_ERROR: An unexpected error occurred while fetching the schema. Details: {str(e)}"

    def execute_raw_query(self, sql_string: str):
        try:
            with self.engine.connect() as connection:
                query = text(sql_string)
                result = connection.execute(query)

            return [dict(row._mapping) for row in result]

        except Exception as e:
            return f"DATABASE_ERROR: {str(e)}"