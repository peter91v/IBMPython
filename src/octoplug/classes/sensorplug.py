import json
import logging


class SensorPlug:
    # Definition der Konstanten für die Positionen der Datenfelder
    ID_POSITION = 0
    SENSORNAME_POSITION = 1
    TEMPERATUR_POSITION = 2
    UHRZEIT_POSITION = 3

    @classmethod
    def convert(cls, data_string):
        data = {}
        for line in data_string.split("\n"):
            line = line.strip('"').split(";")
            if len(line) < 4:
                continue
            sensor_data = {
                "ID": int(line[cls.ID_POSITION]),
                "Sensorname": line[cls.SENSORNAME_POSITION],
                "Temperatur": float(line[cls.TEMPERATUR_POSITION]),
                "Uhrzeit": line[cls.UHRZEIT_POSITION],
            }
            if sensor_data["ID"] not in data:
                data[sensor_data["ID"]] = []
            data[sensor_data["ID"]].append(sensor_data)
        return data
