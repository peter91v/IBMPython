import logging
import os
import datetime
import classes.const as const


class LogHandler:
    def __init__(self, log_name, show_in_console=False):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:  # Überprüfe, ob der Logger bereits Handler hat
            self.log_dir = const.LogPath
            self.setup_logger(log_name, show_in_console)

    def setup_logger(self, log_name, show_in_console):
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d")
        log_filename = os.path.join(self.log_dir, f"{log_name}_{current_datetime}.log")
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        if show_in_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger
