from classes.base.autopersistent import AutoPersistent
from datetime import datetime as dt
from typing import List, Type
import json


class sensor(AutoPersistent):

    def __init__(
        self,
        ID: int = None,
        STANDORTID: int = None,
        TEMPERATURE: float = None,
        NA_DAT: dt = None,
        AE_DAT: dt = None,
    ):
        self._ID = ID
        self._STANDORTID = STANDORTID
        self._TEMPERATURE = TEMPERATURE
        self._NA_DAT = NA_DAT
        self._AE_DAT = AE_DAT
        super().__init__()

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value):
        self._ID = value

    @property
    def STANDORTID(self):
        return self._STANDORTID

    @STANDORTID.setter
    def STANDORTID(self, value):
        self._STANDORTID = value

    @property
    def TEMPERATURE(self):
        return self._TEMPERATURE

    @TEMPERATURE.setter
    def TEMPERATURE(self, value):
        self._TEMPERATURE = value

    @property
    def NA_DAT(self):
        return self._NA_DAT

    @NA_DAT.setter
    def NA_DAT(self, value):
        self._NA_DAT = value

    @property
    def AE_DAT(self):
        return self._AE_DAT

    @AE_DAT.setter
    def AE_DAT(self, value):
        self._AE_DAT = value

    def populate_from_dict(self, data: dict):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def from_detailed_json(cls, json_string: str) -> List["sensor"]:
        data = json.loads(json_string)
        sensors = []

        if not isinstance(data, dict):
            raise ValueError("JSON must represent a dictionary of objects")

        for key, items in data.items():
            if not isinstance(items, list):
                raise ValueError("Each entry in the JSON must be a list of objects")

            for item in items:
                sensor_data = {
                    "STANDORTID": item["STANDORTID"],
                    "TEMPERATURE": item["grad"],
                    "NA_DAT": f"{item['datum']} {item['zeit']}",
                    # "AE_DAT": item.get("AE_DAT"),
                }
                sensor = cls()
                sensor.populate_from_dict(sensor_data)
                sensors.append(sensor)

        return sensors

    # def from_detailed_json(cls, json_string: str) -> List["sensor"]:
    #     data = json.loads(json_string)
    #     sensors = []

    #     if not isinstance(data, dict):
    #         raise ValueError("JSON must represent a dictionary of objects")

    #     for key, item in data.items():
    #         sensor_data = {
    #             "STANDORTID": item["STANDORTID"],
    #             "TEMPERATURE": item["grad"],
    #             "NA_DAT": f"{item['datum']} {item['zeit']}",
    #             "AE_DAT": None,
    #         }
    #         sensor = cls()
    #         sensor.populate_from_dict(sensor_data)
    #         sensors.append(sensor)

    #     return sensors

    # @classmethod
    # def from_historical_data(cls, json_string: str) -> List["sensor"]:
    #     # data = json.loads(json_string)
    #     sensors = []

    #     if not isinstance(json_string, dict):
    #         raise ValueError("JSON must represent a dictionary of objects")

    #     for key, item in json_string.items():
    #         sensor_data = {
    #             "STANDORTID": item["STANDORTID"],
    #             "TEMPERATURE": item["grad"],
    #             "NA_DAT": item["NA_DAT"],
    #             "AE_DAT": None,
    #         }
    #         sensor = cls()
    #         sensor.populate_from_dict(sensor_data)
    #         sensors.append(sensor)

    #     return sensors
