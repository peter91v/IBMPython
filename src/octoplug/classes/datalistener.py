import json
import os
import shutil
import subprocess
import time
from datetime import datetime
import logging
import const as const
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import classes.sensorplug as Sensorplug
from classes.loghandler import LogHandler

# Konfiguriere das Logging
log_handler = LogHandler(os.path.basename(__file__)[:-3])
logger = log_handler.get_logger()


def run_subprocess(json_string: str):
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
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess failed with error: {e.output}")
        return None


class FileHandler(FileSystemEventHandler):
    """
    Behandelt Dateisystem-Events, die von einem Watchdog-Observer erfasst werden.
    """

    def on_created(self, event):
        if event.is_directory:
            return
        logger.info(f"New file detected: {event.src_path}")
        process_file(event.src_path)


def process_file(file_path):
    """
    Verarbeitet die neu erstellte Datei, konvertiert deren Inhalt und sendet ihn an einen externen Prozess.
    """
    logger.info(f"Processing file: {file_path}")
    try:
        with open(file_path, "r") as file:
            file_data = file.read()
        data = Sensorplug.SensorPlug.convert(file_data)
        json_data = json.dumps(data)
        run_subprocess(json_data)
        move_to_archive(file_path)
    except Exception as e:
        logger.error(f"Failed to process file {file_path}: {e}")


def move_to_archive(file_path):
    """
    Verschiebt die verarbeitete Datei in ein Archivverzeichnis, das nach dem aktuellen Datum benannt ist.
    """
    try:
        archive_subfolder = os.path.join(
            const.archive_folder, datetime.now().strftime("%Y-%m-%d")
        )
        if not os.path.exists(archive_subfolder):
            os.makedirs(archive_subfolder)
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        archived_file_name = f"{file_name}_{timestamp}{file_extension}"
        archived_file_path = os.path.join(archive_subfolder, archived_file_name)
        shutil.move(file_path, archived_file_path)
        logger.info(f"Moved file {file_path} to {archived_file_path}")
    except Exception as e:
        logger.error(f"Failed to move file {file_path} to archive: {e}")


if __name__ == "__main__":
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, const.input_folder, recursive=False)
    observer.start()
    logger.info(f"Monitoring directory: {const.input_folder}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        observer.stop()
    observer.join()
