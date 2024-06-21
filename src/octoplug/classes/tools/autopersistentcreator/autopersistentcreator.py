from classes.base.databasecontroller import DatabaseController
from autopersistentgenerator import AutoPersistentGenerator

# host = "localhost"
# user = "root"
# password = "varP91!!"
# database = "temperature"

db_controller = DatabaseController()
db_instance = db_controller.get_instance()
# controller_mysql.connect()

columns = []
columns = db_controller.get_columns("sensor", data_type=True)
print(columns[0]["COLUMN_NAME"])

generator = AutoPersistentGenerator(
    "D:\DEV\PythonProject\src\persistent\classes\persistent", "sensor"
)
generator.create_file(columns)
