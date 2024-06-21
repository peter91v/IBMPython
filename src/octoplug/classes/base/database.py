import mysql.connector


class SingletonDB:
    _instance = None

    def __new__(cls, host, user, password, database):
        if cls._instance is None:
            cls._instance = super(SingletonDB, cls).__new__(cls)
            cls._instance.connection = mysql.connector.connect(
                host=host, user=user, password=password, database=database
            )
        return cls._instance

    def get_connection(self):
        return self._instance.connection
