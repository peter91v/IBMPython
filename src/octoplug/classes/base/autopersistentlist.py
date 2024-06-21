from datetime import datetime, timedelta
import json
from os import path
from classes.base.autopersistent import AutoPersistent
from classes.base.databasecontroller import DatabaseController
from abc import ABC, abstractmethod
from classes.base.jsontools import CustomJSONEncoder
import classes.const as const


class AutoPersistentLst:
    def __init__(self):
        self.db = DatabaseController.get_instance()  # Verwendung der Singleton-Instanz
        self.items = []

    @abstractmethod
    def get_persistent_class(self):
        """Muss von abgeleiteten Klassen implementiert werden, um den Typ der Objekte zu definieren."""
        pass

    def load_all(self):
        """Lädt alle Einträge aus der Datenbank basierend auf dem Typ der AutoPersistent-Objekte."""
        if self.get_persistent_class is None:
            print("Fehler: Kein Typ für das Laden von Objekten angegeben.")
            return

        table_name = self.get_persistent_class().__name__.upper()
        loaded_data = self.db.fetch_data(table_name)
        column_names = self.db.get_columns(table_name)
        # [row[0] for row in column_names] if column_names else []
        for data in loaded_data:
            instance = (
                self.get_persistent_class()()
            )  # Erstellt eine neue Instanz des Objekts
            if isinstance(data, tuple):
                # Hier konvertieren wir das Tuple in ein Dictionary
                # Angenommen, das Tuple hat eine definierte Struktur
                data_dict = self.convert_tuple_to_dict(column_names, data)
                instance.populate_from_dict(data_dict)
            elif isinstance(data, dict):
                instance.populate_from_dict(data)
            self.items.append(instance)

    def convert_tuple_to_dict(self, columns, data_tuple):
        return {str(columns[i][0]): data_tuple[i] for i in range(len(columns))}

    def load(self, id):
        """Lädt ein spezifisches Element basierend auf der ID."""
        self.db.reset_query_conditions()
        primary_key = self.get_primary_key(table_name)
        self.add_where(primary_key, id)
        table_name = self.items[0].__class__.__name__.lower()
        data = self.db.load(table_name)
        if data:
            instance = self.get_persistent_class()()
            instance.populate_from_dict(data[0])
            instance.connection = self.connection
            return instance
        else:
            return None

    def add(self, item, shouldsave=False):
        if type(item).__name__ != self.get_persistent_class().__name__:
            raise ValueError(
                f"Item must be an instance of {self.get_persistent_class().__name__}"
            )
        self.items.append(item)
        if shouldsave:
            item.save()

    def remove(self, id):
        item = self.get_by_id(id)
        if item:
            self.items.remove(item)
            # item.delete()  # Deletes the item from the database
            return True
        return False

    def populate_from_dict(self, data):
        """Bevölkert ein Objekt mit Daten aus einem Dictionary. Diese Methode sollte in der AutoPersistent Klasse definiert sein."""
        for key, value in data.items():
            setattr(self, key, value)

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.items):
            result = self.items[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration

    def get_by_id(self, id):
        for item in self.items:
            if hasattr(item, "id") and item.id == id:
                return item
        return None

    def move_to(self, old_position, new_position):
        if 0 <= old_position < len(self.items) and 0 <= new_position < len(self.items):
            self.items.insert(new_position, self.items.pop(old_position))
        else:
            raise IndexError("Position out of range")

    def get_primary_key(self, table):
        # Funktion, um den Primärschlüssel der Tabelle zu erhalten
        query = f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'"
        result = self.fetch_data(query)
        if result:
            primary_key_column = result[0][
                "Column_name"
            ]  # Spaltenname des Primärschlüssels
            return primary_key_column
        else:
            return None

    def count(self):
        """Gibt die Anzahl der Objekte in der Liste zurück."""
        return len(self.items)

    def save_all(self):
        """Speichert alle Objekte in der Liste in der Datenbank."""
        for item in self.items:
            item.save()

    def save_all_to_json(self, directory, filename=None):
        data_list = {}
        data_list = [item.to_dict() for item in self.items]
        if not filename:
            filename = f"All_{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = path.join(directory, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(
                data_list, file, cls=CustomJSONEncoder, ensure_ascii=False, indent=4
            )
        print(f"Alle Daten wurden in {filepath} gespeichert.")

    def populate_from_json(self, json_string):
        # Parsen des JSON-Strings in eine Python-Liste von Dictionaries

        data = json.loads(json_string)

        # Ermittle die Klasse der persistenten Objekte

        # Überprüfen, ob die Datenstruktur ein Dictionary oder eine Liste ist
        persistent_class = self.get_persistent_class()
        if isinstance(data, dict):
            data_list = [data]
        elif isinstance(data, list):
            data_list = data
        else:
            raise ValueError("JSON must represent an object or an array of objects")

        # # Erstelle und befülle Objekte für jedes Dictionary in der Liste
        # for key, item in data.items():
        #     # Überprüfe, ob die abgeleitete Klasse eine `populate_from_dict` Methode hat
        #     if hasattr(persistent_class, "populate_from_dict"):
        #         obj = persistent_class()
        #         sensor_data = {
        #             "ID": int(key),
        #             "STANDORTID": item["code"],
        #             "TEMPERATURE": item["grad"],
        #             "NA_DAT": f"{item['datum']} {item['zeit']}",
        #             "AE_DAT": None,
        #         }
        #         obj.populate_from_dict(sensor_data)
        #         self.items.append(obj)
        #     else:
        #         raise NotImplementedError(
        #             "Die Klasse muss eine `populate_from_dict` Methode implementieren."
        #         )
        sensors = persistent_class.from_detailed_json(json_string)
        self.items.extend(sensors)

    # def process_and_save_historical_data(self, json_string: str):
    #     data = json.loads(json_string)
    #     print(json_string)
    #     print("data: ", data)
    #     # Überprüfen, ob die Datenstruktur ein Dictionary oder eine Liste ist
    #     persistent_class = self.get_persistent_class()
    #     sensors = persistent_class.from_historical_data(data)
    #     self.items.extend(sensors)
