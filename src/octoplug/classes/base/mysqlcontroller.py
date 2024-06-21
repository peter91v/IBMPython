import mysql.connector
from src.persistent.classes.base.databasecontrollerbase import DatabaseControllerBase


class MySQLController(DatabaseControllerBase):
    def initialize(self, config):
        if not self.initialized:
            try:
                self.connection = mysql.connector.connect(
                    host=config["host"],
                    user=config["user"],
                    password=config["password"],
                    database=config["database"],
                )
                self.initialized = True
                self.Log.info("Datenbankverbindung hergestellt")
            except mysql.connector.Error as e:
                self.Log.error(f"Fehler bei der Verbindung zur Datenbank: {e}")
                self.initialized = False

    def execute_query(self, query, params=None):
        query_type = query.strip().upper()
        params = params or self.params
        result = None
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                if query_type.startswith("SELECT") or query_type.startswith("SHOW"):
                    result = cursor.fetchall()
                    self.Log.info(
                        f"Query executed: {query}, {len(result)} rows fetched."
                    )
                else:
                    self.connection.commit()
                    self.Log.info("Abfrage erfolgreich ausgeführt")
        except mysql.connector.Error as e:
            self.Log.error(f"Fehler beim Ausführen der Abfrage: {e}")
            self.connection.rollback()
            raise e
        finally:
            self.reset_query_conditions()
        return result

    def insert_data(self, table, columns, values):
        placeholders = ", ".join(["%s"] * len(values))
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        self.execute_query(query, values)
