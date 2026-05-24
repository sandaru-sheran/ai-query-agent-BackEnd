from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from core import Database


class AIAgentRepository:

    def get_database_schema(self):
        database_map = []
        session = Database.get_db()

        try:
            # 1. Get the engine from the current session
            engine = session.get_bind()

            # 2. Create the SQLAlchemy Inspector
            inspector = inspect(engine)

            # 3. Get all table names (works on ANY database)
            table_names = inspector.get_table_names()

            for table in table_names:
                # 4. Get the columns for each table
                columns = inspector.get_columns(table)

                columns_info = []
                for col in columns:
                    columns_info.append({
                        "name": col["name"],
                        # Convert the SQLAlchemy Type object to a string so FastAPI can return it as JSON
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True),
                        "primary_key": col.get("primary_key", 0) > 0  # Some dialects return 1 for PK
                    })

                database_map.append({
                    "table_name": table,
                    "columns": columns_info
                })

            return {"database": database_map}

        except SQLAlchemyError as e:
            return f"DATABASE_ERROR: Failed to retrieve schema. Details: {str(e)}"

        except Exception as e:
            return f"SYSTEM_ERROR: An unexpected error occurred while fetching the schema. Details: {str(e)}"

        finally:
            session.close()

    def execute_raw_query(self, sql_string: str):
        databse = Database.get_db()
        try:
            with databse as connection:
                query = text(sql_string)
                result = connection.execute(query)

            return [dict(row._mapping) for row in result]

        except Exception as e:
            return f"DATABASE_ERROR: {str(e)}"