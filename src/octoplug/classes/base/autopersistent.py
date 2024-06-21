from datetime import datetime, date, time
import json
from os import path
import psycopg2
import inspect
from classes.base.databasecontroller import (
    DatabaseController,
)
from abc import ABC


class AutoPersistent(ABC):
    def __init__(self):
        self.db = DatabaseController.get_instance()
        self._NA_DAT = None
        self._AE_DAT = None

    def create_table(self):
        cursor = self.db.connection.cursor()
        table_name = self.__class__.__name__.lower()
        columns = inspect.getmembers(self.__class__, lambda x: isinstance(x, property))
        columns = [c[0] for c in columns]
        columns_str = ", ".join([f"{c} TEXT" for c in columns])
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY, {columns_str})"
        print(create_table_sql)
        cursor.execute(create_table_sql)
        self.db.connection.commit()

    def save(self):
        if not self.db.connection:
            print(f"Error: No database connection for class {self.__class__.__name__}")
            return None

        table_name = self.__class__.__name__.lower()
        primary_key = self.get_primary_key(table_name)
        if not primary_key:
            print(f"Error: Primary key not found for table {table_name}")
            return None

        # Überprüfen, ob der Eintrag bereits in der Datenbank vorhanden ist
        where_clause = f'"{primary_key}" = %s'
        params = (getattr(self, primary_key),)
        existing_entry = self.db.fetch_data(table_name, "*", where_clause, params)

        if existing_entry:
            # Eintrag existiert bereits, daher ein UPDATE durchführen
            self.AE_DAT = datetime.now()
            columns = self.getColumns()
            set_clause = ", ".join(
                [f'"{col}" = %s' for col in columns if col != primary_key]
            )
            update_params = [
                getattr(self, col) for col in columns if col != primary_key
            ]
            update_params.append(getattr(self, primary_key))
            try:
                self.db.update_data(table_name, set_clause, where_clause, update_params)
            except psycopg2.Error as e:
                print(f"Fehler bei der Update: {e}")
                return None
        else:
            # Eintrag existiert nicht, daher ein INSERT durchführen
            # self.NA_DAT = datetime.now() muss wieder aktiviert werden wenn alle Historische Daten verarbeitet worden sind
            columns = self.getColumns()
            values = [getattr(self, c) for c in columns]
            try:
                self.db.insert_data(table_name, columns, values)
            except psycopg2.Error as e:
                print(f"Fehler bei der Insert: {e}")
                return None

    def key(self, var):
        return str(var)

    def get_primary_key(self, table):
        query = f"SELECT kcu.column_name FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name WHERE tc.table_name = '{table.upper()}' AND tc.constraint_type = 'PRIMARY KEY';"
        result = self.db.execute_query(query)
        if result:
            primary_key_column = result[0]["column_name"]
            return primary_key_column
        else:
            return None

    def load(self, id):
        if not self.db.connection:
            print(f"Error: No database connection for class {self.__class__.__name__}")
            return None

        table_name = self.__class__.__name__.lower()
        primary_key = self.get_primary_key(table_name)
        if not primary_key:
            print(f"Error: Primary key not found for table {table_name}")
            return None

        columns = "*"  # Alle Spalten auswählen
        where_clause = f'"{primary_key}" = %s'
        params = (id,)
        rows = self.db.fetch_data(table_name, columns, where_clause, params)

        if not rows:
            print(f"Error: No entry with ID {id} found in table {table_name}")
            return None

        row = rows[0]
        instance = self.__class__()
        self.populate_from_dict(row)
        return self

    def delete_data_by_id(self, table, id_value):
        primary_key = self.get_primary_key(table)
        if not primary_key:
            print(f"Error: Primary key not found for table {table}")
            return

        query = f'DELETE FROM "{table}"" WHERE "{primary_key}" = %s'
        self.db.execute_query(query, (id_value,))

    def delete(self):
        primary_key = self.get_primary_key(self.__class__.__name__.lower())
        if not primary_key:
            print("Error: Primary key not found for the table")
            return

        id_value = getattr(self, primary_key)
        if id_value is not None:
            query = f"DELETE FROM {self.__class__.__name__.lower()} WHERE {primary_key} = %s"
            self.db.execute_query(query, (id_value,))
            print(f"Record with {primary_key}={id_value} deleted.")
        else:
            print(f"Error: {primary_key} attribute not set for the instance.")

    def getColumns(self):
        columns = [
            attr.lstrip("_")
            for attr in vars(self).keys()
            if not attr.startswith("__") and attr not in ["db", "connection"]
        ]
        return columns

    def populate_from_dict(self, data):
        for key, value in data.items():
            attr_name = f"_{key}"
            if hasattr(self, attr_name):
                setattr(self, attr_name, value)

    def to_dict(self):
        data_dict = {}
        for attribute, value in vars(self).items():
            clean_attribute = attribute.lstrip("_")
            if isinstance(value, datetime):
                data_dict[clean_attribute] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, date):
                data_dict[clean_attribute] = value.strftime("%Y-%m-%d")
            elif isinstance(value, time):
                data_dict[clean_attribute] = value.strftime("%H:%M:%S")
            elif isinstance(value, DatabaseController):
                continue
            else:
                data_dict[clean_attribute] = value
        return data_dict

    def save_to_json(self, directory, filename=None):
        data_dict = self.to_dict()
        if not filename:
            filename = f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = path.join(directory, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data_dict, file, ensure_ascii=False, indent=4)
        print(f"Daten wurden in {filepath} gespeichert.")
