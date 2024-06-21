import os
from src.persistent.classes.base.externalfilehaendler import ExternalFileHandler
from src.persistent.classes.base.loghandler import LogHandler


class DatabaseControllerBase:
    _instance = None
    Log = LogHandler(os.path.basename(__file__)[:-3], show_in_console=True).get_logger()
    Config = ExternalFileHandler().load_database_config()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseControllerBase, cls).__new__(cls)
            cls._instance.initialized = False
            cls._instance.connection = None
            cls._instance.where_clause = ""
            cls._instance.params = []
        return cls._instance

    @classmethod
    def get_instance(cls, db_type="postgresql"):
        if cls._instance is None:
            # Standardmäßig PostgreSQL verwenden
            config = cls.Config.get(db_type)

            if config is None:
                raise ValueError(f"No configuration found for database type: {db_type}")

            if db_type == "mysql":
                from src.persistent.classes.base.mysqlcontroller import MySQLController

                cls._instance = MySQLController()
            elif db_type == "postgresql":
                from src.persistent.classes.base.postgrescontroller import (
                    PostgresController,
                )

                cls._instance = PostgresController()
            else:
                raise ValueError("Unsupported database type")

            if not cls._instance.initialized:
                cls._instance.initialize(config)
        return cls._instance

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
        query = f"SELECT {columns} FROM {table}"
        if where_clause or self.where_clause:
            query += (
                f" WHERE {self.where_clause if self.where_clause else where_clause}"
            )
        return self.execute_query(query, params or self.params)

    def update_data(self, table, set_clause, where_clause=None, params=None):
        query = f"UPDATE {table} SET {set_clause}"
        if where_clause or self.where_clause:
            query += (
                f" WHERE {self.where_clause if self.where_clause else where_clause}"
            )
        self.execute_query(query, params or self.params)

    def delete_data(self, table, where_clause=None, params=None):
        query = f"DELETE FROM {table}"
        if where_clause or self.where_clause:
            query += (
                f" WHERE {self.where_clause if self.where_clause else where_clause}"
            )
        self.execute_query(query, params or self.params)

    def get_columns(self, table_name, data_type=False):
        if data_type:
            result = self.fetch_data(
                "INFORMATION_SCHEMA.COLUMNS",
                "COLUMN_NAME, DATA_TYPE",
                f"TABLE_NAME='{table_name}'",
            )
        else:
            result = self.fetch_data(
                "INFORMATION_SCHEMA.COLUMNS",
                "COLUMN_NAME",
                f"TABLE_NAME='{table_name}'",
            )
        if result:
            return result
        else:
            return None

    def execute_query(self, query, params=None):
        raise NotImplementedError("Subclasses should implement this method")

    def initialize(self, config):
        raise NotImplementedError("Subclasses should implement this method")

    def insert_data(self, table, columns, values):
        raise NotImplementedError("Subclasses should implement this method")
