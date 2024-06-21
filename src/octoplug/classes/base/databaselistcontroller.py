import json
import sqlite3
import mysql.connector


class DatabaseListController:
    def __init__(self, host=None, user=None, password=None, database=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self.db_connection = None
        self.where_clause = ""
        self.params = []  # Initialisiere params im Konstruktor
        self.items = []

    def connect(self, connection=None):
        if connection:
            self.connection = connection
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
        else:
            try:
                if self.db_connection is None:
                    self.connection = mysql.connector.connect(
                        host=self.host,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                    )
                else:
                    self.connection = self.db_connection
                if self.connection.is_connected():
                    self.cursor = self.connection.cursor()
                    print("Verbindung zur Datenbank hergestellt")
            except mysql.connector.Error as e:
                print(f"Fehler bei der Verbindung zur Datenbank: {e}")
                return None

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Verbindung zur Datenbank getrennt")

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.connection.commit()
                print("Abfrage erfolgreich ausgeführt")
        except mysql.connector.Error as e:
            print(f"Fehler beim Ausführen der Abfrage: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def fetch_data(self, query):
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, self.params)  # Nutze self.params direkt
                rows = cursor.fetchall()
            return rows
        finally:
            self.reset_query_conditions()  # Reset nach der Abfrage

    def load(self, table, columns="*"):
        query = f"SELECT {columns} FROM {table}"
        if self.where_clause:
            query += f" WHERE {self.where_clause}"
        return self.fetch_data(query)

    def add_where(self, key, value):
        param_placeholder = "%s"
        if self.where_clause != "":
            self.where_clause += f" AND {key} = {param_placeholder}"
        else:
            self.where_clause = f"{key} = {param_placeholder}"
        self.params.append(value)

    def reset_query_conditions(self):
        self.where_clause = ""
        self.params = []

    def get_persistent_class(self):
        """
        Diese Methode sollte in abgeleiteten Klassen überschrieben werden,
        um die Klasse der persistenten Objekte zurückzugeben.
        """
        raise NotImplementedError(
            "Diese Methode sollte in einer abgeleiteten Klasse überschrieben werden."
        )

