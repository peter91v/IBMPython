import json
import os
import subprocess
import logging
import const as const
from classes.loghandler import LogHandler


# Konfiguriere das Logging
log_handler = LogHandler(os.path.basename(__file__)[:-3])
logger = log_handler.get_logger()

class SensorPlug:
    @classmethod
    def convert(cls, line):
        try:
            parts = line.split("|")
            if len(parts) != 3:
                raise ValueError(f"Line does not contain exactly 3 parts: {line}")

            datum = parts[0]
            time = parts[1]
            measurements_str = parts[2]

            measurements = json.loads(measurements_str.replace("'", '"'))
            all_data = {}

            for sensor_id, temperature in measurements.items():
                sensor_data = {
                    "STANDORTID": int(sensor_id),
                    "grad": float(temperature),
                    "datum": datum,
                    "zeit": time,
                    "AE_DAT": None,
                }
                if sensor_id not in all_data:
                    all_data[sensor_id] = []
                all_data[sensor_id].append(sensor_data)

            return json.dumps(all_data, indent=4)
        except ValueError as e:
            logger.error(f"Error parsing line: {line}")
            logger.error(f"Exception: {e}")
            return None

    @classmethod
    def process_file(cls, file_path):
        """
        Verarbeitet die neu erstellte Datei, konvertiert deren Inhalt und sendet ihn an einen externen Prozess.
        """
        logger.info(f"Processing file: {file_path}")

        try:
            with open(file_path, "r") as file:
                buffer = []
                for line in file:
                    buffer.append(line.strip())
                    if len(buffer) == 5:
                        cls.process_lines(buffer)
                        buffer.clear()
                if buffer:
                    cls.process_lines(buffer)
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")

    @classmethod
    def process_lines(cls, lines):
        """
        Verarbeitet eine Liste von Zeilen und sendet sie an einen externen Prozess.
        """
        combined_data = {}
        for line in lines:
            converted = cls.convert(line)
            if converted:
                json_data = json.loads(converted)
                for key, value in json_data.items():
                    if key not in combined_data:
                        combined_data[key] = []
                    combined_data[key].extend(value)

        json_payload = json.dumps(combined_data)
        logger.info(f"Processing lines: {lines}")
        logger.info(f"Converted JSON data: {json_payload}")
        if not cls.run_subprocess(json_payload):
            logger.error(f"Failed to process lines: {lines}")

    @classmethod
    def run_subprocess(cls, json_string: str):
        """
        Führt einen externen Prozess mit dem gegebenen JSON-String als Parameter aus.
        """
        try:
            result = subprocess.run(
                [
                    const.python_executable,
                    const.octo_client_path,
                    str(const.ServerPort),
                    json_string,
                    "SendMessage",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logger.info(f"Subprocess output: {result.stdout}")
            if result.stderr:
                logger.error(f"Subprocess error: {result.stderr}")
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            logger.error(f"Subprocess failed with error: {e.stderr}")
            return False
