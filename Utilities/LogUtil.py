import logging
import os
import time


class Logger():

    def __init__(self, logger, file_level=logging.INFO):
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        fmt = logging.Formatter('%(asctime)s - %(filename)s:[%(lineno)s] - [%(levelname)s] - %(message)s')

        curr_time = time.strftime("%Y-%m-%d")
        # Project-root/Logs, independent of the working directory and OS path separator
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Logs")
        os.makedirs(log_dir, exist_ok=True)
        self.LogFileName = os.path.join(log_dir, 'log' + curr_time + '.txt')

        # Avoid duplicate lines when the same logger name is created more than once
        if any(isinstance(h, logging.FileHandler) and h.baseFilename == os.path.abspath(self.LogFileName)
               for h in self.logger.handlers):
            return
        # "a" to append the logs in same file, "w" to generate new logs and delete old one
        fh = logging.FileHandler(self.LogFileName, mode="a")
        fh.setFormatter(fmt)
        fh.setLevel(file_level)
        self.logger.addHandler(fh)
