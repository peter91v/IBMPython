import psycopg2
from psycopg2 import sql, extras
from src.persistent.classes.base.databasecontrollerbase import DatabaseControllerBase


class PostgresController(DatabaseControllerBase):
    def initialize(self, config):
        if not self.initialized:
            try:
                self.connection = psycopg2.connect(
                    host=config["host"],
                    user=config["user"],
                    password=config["password"],
                    database=config["database"],
                )
                self.initialized = True
                self.Log.info("Datenbankverbindung hergestellt")
            except psycopg2.Error as e:
                self.Log.error(f"Fehler bei der Verbindung zur Datenbank: {e}")
                self.initialized = False

    def execute_query(self, query, params=None):
        query_string = (
            query.as_string(self.connection)
            if isinstance(query, sql.Composed)
            else query
        )
        if isinstance(query_string, str):
            query_type = query_string.strip().split()[0].upper()
        params = params or self.params
        result = None
        try:
            with self.connection.cursor(cursor_factory=extras.RealDictCursor) as cursor:
                cursor.execute(query_string, params)
                if query_type in ["SELECT", "SHOW"]:
                    result = cursor.fetchall()
                    self.Log.info(
                        f"Query executed: {query_string}, {len(result)} rows fetched."
                    )
                else:
                    if query_type == "INSERT":
                        result = cursor.fetchone()  # Return the ID of the inserted row
                    self.connection.commit()
                    self.Log.info("Abfrage erfolgreich ausgeführt")
        except psycopg2.Error as e:
            self.Log.error(f"Fehler beim Ausführen der Abfrage: {e}")
            self.connection.rollback()
            raise e
        finally:
            self.reset_query_conditions()
        return result

    def insert_data(self, table, columns, values):
        filtered_columns_values = [
            (col, val) for col, val in zip(columns, values) if val is not None
        ]
        if not filtered_columns_values:
            raise ValueError("Es wurden keine Werte zum Einfügen angegeben.")
        filtered_columns, filtered_values = zip(*filtered_columns_values)
        formatted_columns = [sql.Identifier(col.upper()) for col in filtered_columns]
        placeholders = sql.SQL(", ").join(sql.Placeholder() * len(filtered_values))
        query = sql.SQL(
            "INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING id"
        ).format(
            table=sql.Identifier(table.upper()),
            fields=sql.SQL(", ").join(formatted_columns),
            values=placeholders,
        )
        return self.execute_query(query, filtered_values)
