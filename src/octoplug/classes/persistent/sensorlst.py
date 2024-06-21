from classes.base.autopersistentlist import AutoPersistentLst
from classes.persistent.sensor import sensor


class sensorlst(AutoPersistentLst):

    def __init__(self):
        super().__init__()

    def get_persistent_class(self):
        return sensor

    def add(self, sensor):
        self.add(sensor)

    def remove_by_id(self, id):
        self.remove(id)

    def find_by_id(self, id):
        return self.get_by_id(id)

    def load_all_sensor(self):
        self.load_all()

    def update_sensor(self, sensor):
        pass  # Sensor-Objekt zu aktualisieren
