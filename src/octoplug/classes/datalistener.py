import os
import sys
import threading
import time
import logging
import shutil  # Importieren von shutil für Dateibewegungen
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import const as const
import psutil
from classes.loghandler import LogHandler
from classes.sensorplug import SensorPlug  # Importieren Sie die SensorPlug-Klasse

try:
    if os.name == "nt":
        import win32api
        import win32con
        import win32console
except ImportError:
    win32api = None
    win32con = None
    win32console = None

try:
    from setproctitle import setproctitle
except ImportError:
    setproctitle = None

# Konfiguriere das Logging
log_handler = LogHandler(os.path.basename(__file__)[:-3])
logger = log_handler.get_logger()

# Name des Prozesses setzen
if os.name == "nt" and win32console:
    win32console.SetConsoleTitle("datalistener")
elif setproctitle:
    setproctitle("datalistener")

# PID-Datei definieren
PID_DIR = os.path.join(os.path.dirname(__file__), "pids")
PID_FILE = os.path.join(PID_DIR, "datalistener.pid")


def check_if_running():
    """
    Überprüft, ob das Skript bereits läuft.
    """
    if not os.path.exists(PID_DIR):
        os.makedirs(PID_DIR)

    if os.path.isfile(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                logger.error("Skript läuft bereits. Beende...")
                sys.exit(1)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


def remove_pid_file():
    """
    Entfernt die PID-Datei beim Beenden des Skripts.
    """
    if os.path.isfile(PID_FILE):
        os.remove(PID_FILE)


def wait_for_file_access(file_path, timeout=5):
    """
    Wartet darauf, dass die Datei zugänglich ist, bis der Timeout erreicht ist.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with open(file_path, "r"):
                return True
        except IOError:
            time.sleep(0.5)
    return False


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
    if not wait_for_file_access(file_path):
        logger.error(f"Failed to access file {file_path}: Permission denied")
        return

    try:
        SensorPlug.process_file(
            file_path
        )  # Übergabe der Datei zur Verarbeitung an SensorPlug
        logger.info(f"Finished processing file: {file_path}")

        # Kurze Verzögerung einfügen, um sicherzustellen, dass die Datei nicht mehr verwendet wird
        time.sleep(1)
        move_to_archive(file_path)
    except Exception as e:
        logger.error(f"Failed to process file {file_path}: {e}")


def process_existing_files(directory):
    """
    Diese Funktion verarbeitet alle vorhandenen Dateien im Verzeichnis und überprüft dann,
    ob während der Verarbeitung neue Dateien hinzugekommen sind.
    Dies wird in einer Schleife wiederholt, bis keine neuen Dateien mehr gefunden werden.

    """
    while True:
        files_processed = False
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if os.path.isfile(file_path):
                process_file(file_path)
                files_processed = True

        if not files_processed:
            break


def restart_program():
    """
    Startet das aktuelle Programm neu.
    Beendet das aktuelle Programm und startet es neu.
    """
    try:
        logger.info("Restarting the program...")
        remove_pid_file()
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        logger.error(f"Failed to restart the program: {e}")


def schedule_restart_at_midnight():
    """
    Plant den Neustart des Programms um Mitternacht.
    Berechnet die Zeit bis Mitternacht und startet einen Timer, der das Programm neu startet.
    """
    now = datetime.now()
    next_midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    time_until_midnight = (next_midnight - now).total_seconds()

    logger.info(f"Scheduling restart in {time_until_midnight} seconds.")
    threading.Timer(time_until_midnight, restart_program).start()


if __name__ == "__main__":
    check_if_running()

    # Verarbeite vorhandene Dateien im Verzeichnis
    process_existing_files(const.input_folder)

    # Plane den Neustart um Mitternacht, unteranderem ist es nötig damit die Logs neu erstellt werden mit der richtige Datum
    schedule_restart_at_midnight()

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
    remove_pid_file()
