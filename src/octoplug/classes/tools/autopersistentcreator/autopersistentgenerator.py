class AutoPersistentGenerator:
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.class_definition = []
        self.IsList = False

    def map_column_type(self, postgres_type):
        # Mapping dictionary for PostgreSQL to Python types
        postgresql_to_python = {
            "bigint": "int",
            "bigserial": "int",
            "bit": "str",
            "bit varying": "str",
            "boolean": "bool",
            "box": "str",
            "bytea": "bytes",
            "character": "str",
            "character varying": "str",
            "cidr": "str",
            "circle": "str",
            "date": "dt.date",
            "double precision": "float",
            "inet": "str",
            "integer": "int",
            "interval": "dt.timedelta",
            "json": "dict",
            "jsonb": "dict",
            "line": "str",
            "lseg": "str",
            "macaddr": "str",
            "money": "str",
            "numeric": "decimal.Decimal",
            "path": "str",
            "pg_lsn": "str",
            "point": "str",
            "polygon": "str",
            "real": "float",
            "smallint": "int",
            "smallserial": "int",
            "serial": "int",
            "text": "str",
            "time": "dt.time",
            "time without time zone": "dt.time",
            "time with time zone": "dt.time",
            "timestamp": "dt.datetime",
            "timestamp without time zone": "dt.datetime",
            "timestamp with time zone": "dt.datetime",
            "tsquery": "str",
            "tsvector": "str",
            "txid_snapshot": "str",
            "uuid": "str",
            "xml": "str",
        }

        return postgresql_to_python.get(
            postgres_type, "str"
        )  # Default to "str" if type is not found

    def create_file(self, columns):
        file_path = f"{self.path}/{self.name.lower()}.py"
        try:
            with open(file_path, "w") as file:
                self.generate_class(columns)
                for class_def in self.class_definition:
                    file.write("%s\n" % class_def)
            print(f"Die Datei {self.name} wurde erfolgreich erstellt.")
            self.IsList = True
            self.class_definition.clear()
            file_path = f"{self.path}/{self.name.lower()}lst.py"
            with open(file_path, "w") as file:
                self.generate_class(columns)
                for class_def in self.class_definition:
                    file.write("%s\n" % class_def)
            print(f"Die Datei {self.name}lst wurde erfolgreich erstellt.")
        except Exception as e:
            print(f"Fehler beim Erstellen der Datei {self.name}lst: {e}")

    def add_imports(self):
        """Fügt den Imports von DBController und datetime hinzu."""
        if self.IsList:
            return f"from src.persistent.classes.base.autopersistentlist import AutoPersistentLst\nfrom src.persistent.classes.persistent.{self.name.lower()} import {self.name.lower()} \n\n"
        else:
            return "from src.persistent.classes.base.autopersistent import AutoPersistent\nfrom datetime import datetime as dt\n\n"

    def generate_class(self, columns):
        if self.IsList:
            self.class_definition.append(self.add_imports())
            self.class_definition.append(f"class {self.name}Lst(AutoPersistentLst):\n")
            self.class_definition.append("    def __init__(self):\n")
            self.class_definition.append("        super().__init__()\n")
            self.generate_methods()
        else:
            self.class_definition.append(self.add_imports())
            self.class_definition.append(f"class {self.name}(AutoPersistent):\n")
            self.class_definition.append("    def __init__(self,\n")
            self.add_columns(columns)
            self.generate_getter_and_setter(columns)

    def add_columns(self, columns):
        """Adds class variables for each column in the given dictionary."""
        colname = ""
        for col in columns:
            colname = col[0]
            column_type = self.map_column_type(col[1])
            print(f"Column: {col[0]}, Type: {column_type}")
            class_variable = f"        {colname}: {column_type} = None,"
            self.class_definition.append(class_variable)
        self.class_definition.append("    ):")
        for col in columns:
            colname = col[0]
            self.class_definition.append(f"        self._{colname} = {colname}")

        self.class_definition.append("        super().__init__()\n")

    def determine_type(self, data_type):
        types = {
            "date": "dt.date",
            "varchar": "str",
            "varchar2": "str",
            "time": "dt.time",
            "float": "float",
            "int": "int",
        }
        return types.get(data_type, "str")  # Default to str if type is not found

    def generate_getter_and_setter(self, columns):
        for col in columns:
            colname = col[0]
            self.class_definition.append(
                f"    @property\n    def {colname}(self):\n        return self._{colname}\n"
            )
            self.class_definition.append(
                f"    @{colname}.setter\n    def {colname}(self, value):\n        self._{colname} = value\n"
            )

    def generate_methods(self):
        """Generates methods to manage a list of persistent objects."""
        self.class_definition.append(
            f"    def get_persistent_class(self):\n        return {self.name}\n"
        )
        self.class_definition.append(
            f"    def add(self, {self.name}):\n        self.add({self.name})\n"
        )
        self.class_definition.append(
            "    def remove_by_id(self, id):\n         self.remove(id)\n"
        )
        self.class_definition.append(
            "    def find_by_id(self, id):\n         return self.get_by_id(id)\n"
        )
        self.class_definition.append(
            "    def load_all(self):\n         self.load_all()\n"
        )
        self.class_definition.append(
            f"    def update_sensor(self, {self.name}):\n"
            "        pass  # Sensor-Objekt zu aktualisieren\n"
        )
