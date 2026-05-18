from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import uni_engine


class AIAgentRepository:
    def __init__(self):
        self.engine = uni_engine


    def get_database_schema(self):
        database_map = []

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


    def execute_raw_query(self, sql_string: str, parameters: dict = None):
        try:
            with self.engine.begin() as connection:
                query = text(sql_string)

                if parameters:
                    result = connection.execute(query, parameters)
                else:
                    result = connection.execute(query)

                if result.returns_rows:
                    return [dict(row._mapping) for row in result]

        except SQLAlchemyError as e:
            print(f"Database execution error: {e}")
            return {"status": "error", "message": str(e)}