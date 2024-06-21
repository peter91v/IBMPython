import os
import psycopg2
from psycopg2 import sql, extras
from classes.base.externalfilehaendler import ExternalFileHandler
from classes.base.loghandler import LogHandler

ConnectionData = ExternalFileHandler().load_database_config()


class DatabaseController:
    _instance = None
    Log = LogHandler(os.path.basename(__file__)[:-3], show_in_console=True).get_logger()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseController, cls).__new__(cls)
            cls._instance.initialized = False
            cls._instance.connection = None
            cls._instance.where_clause = ""
            cls._instance.params = []
        return cls._instance

    def initialize(self):
        if not self.initialized:
            try:
                self.connection = psycopg2.connect(
                    host=ConnectionData["postgresql"]["host"],
                    user=ConnectionData["postgresql"]["user"],
                    password=ConnectionData["postgresql"]["password"],
                    database=ConnectionData["postgresql"]["database"],
                )
                self.initialized = True
                self.Log.info("Datenbankverbindung hergestellt")
            except psycopg2.Error as e:
                self.Log.error(f"Fehler bei der Verbindung zur Datenbank: {e}")
                self.initialized = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        if not cls._instance.initialized:
            cls._instance.initialize()
        return cls._instance

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
                    self.connection.commit()
                    self.Log.info("Abfrage erfolgreich ausgeführt")
        except psycopg2.Error as e:
            self.Log.error(f"Fehler beim Ausführen der Abfrage: {e}")
            self.connection.rollback()
        finally:
            self.reset_query_conditions()

        return result

    def reset_query_conditions(self):
        self.where_clause = ""
        self.params = []

    def add_where(self, key, value):
        placeholder = "%s"
        if self.where_clause:
            self.where_clause += f" AND {key} = {placeholder}"
        else:
            self.where_clause = f"{key} = {placeholder}"
        self.params.append(value)

    def fetch_data(self, table, columns="*", where_clause=None, params=None):
        if table.lower() == "information_schema.columns":
            query = f"SELECT {columns} FROM {table}"
            if where_clause or self.where_clause:
                query += (
                    f" WHERE {self.where_clause if self.where_clause else where_clause}"
                )
        else:
            table = table.upper()
            columns = columns.upper() if columns != "*" else "*"
            query = sql.SQL("SELECT {fields} FROM {table}").format(
                fields=sql.SQL(columns), table=sql.Identifier(table)
            )
            if where_clause or self.where_clause:
                query += sql.SQL(" WHERE ") + sql.SQL(where_clause or self.where_clause)
        return self.execute_query(query, params or self.params)

    def update_data(self, table, set_clause, where_clause=None, params=None):
        table = table.upper()
        query = sql.SQL("UPDATE {table} SET {set_clause}").format(
            table=sql.Identifier(table), set_clause=sql.SQL(set_clause)
        )
        if where_clause or self.where_clause:
            query += sql.SQL(" WHERE ") + sql.SQL(where_clause or self.where_clause)
        self.execute_query(query, params or self.params)

    def delete_data(self, table, where_clause=None, params=None):
        table = table.upper()
        query = sql.SQL("DELETE FROM {table}").format(table=sql.Identifier(table))
        if where_clause or self.where_clause:
            query += sql.SQL(" WHERE ") + sql.SQL(where_clause or self.where_clause)
        self.execute_query(query, params or self.params)

    def insert_data(self, table, columns, values):
        filtered_columns_values = [
            (col, val) for col, val in zip(columns, values) if val is not None
        ]
        if not filtered_columns_values:
            raise ValueError("Es wurden keine Werte zum Einfügen angegeben.")
        filtered_columns, filtered_values = zip(*filtered_columns_values)
        formatted_columns = [sql.Identifier(col.upper()) for col in filtered_columns]
        placeholders = sql.SQL(", ").join(sql.Placeholder() * len(filtered_values))
        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
            table=sql.Identifier(table.upper()),
            fields=sql.SQL(", ").join(formatted_columns),
            values=placeholders,
        )
        self.execute_query(query, filtered_values)

    def get_columns(self, table_name, data_type=False):
        columns = "COLUMN_NAME, DATA_TYPE" if data_type else "COLUMN_NAME"
        where_clause = f"TABLE_NAME = %s"
        params = (table_name.upper(),)
        return self.fetch_data(
            "information_schema.columns", columns, where_clause, params
        )
