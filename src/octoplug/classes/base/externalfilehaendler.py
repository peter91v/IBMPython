import json
import os

DataPath = "/home/metropol/Dev/test/gRCP/Data"
ConfigPath = "/home/metropol/Dev/test/gRCP/src/config"
DBConfigFilename = "/home/metropol/Dev/test/gRCP/src/config/DB_Config.json"
LogDir = "/home/metropol/Dev/test/gRCP/Log"


class ExternalFileHandler:
    def __init__(self):
        # Hier könnten Initialisierungen stehen, falls nötig
        pass

    def save_to_json(self, data, filename):
        with open(filename, "w") as f:
            json.dump(data, f)

    def load_from_json(self, filename):
        with open(filename, "r") as f:
            return json.load(f)

    def save(self, data, filename):
        with open(filename, "w") as f:
            f.write(data)

    def load(self, filename):
        with open(filename, "r") as f:
            return f.read()

    def delete(self, filename):
        if os.path.exists(filename):
            os.remove(filename)
        else:
            print(f"File {filename} not found.")

    def load_config(self, ConfigPath):
        # Diese Funktion könnte erweitert werden, um spezifische Formate zu unterstützen
        return self.load_from_json(ConfigPath)

    def load_database_config(self, db_config_filename=None):
        # Beispiel für das Laden spezifischer DB-Konfigurationen
        if db_config_filename:
            return self.load_from_json(db_config_filename)
        else:
            return self.load_from_json(DBConfigFilename)

    @classmethod
    def get_log_dir_path(self):
        return LogDir
