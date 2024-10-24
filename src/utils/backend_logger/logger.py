import inspect
import logging
import os
from datetime import datetime

from src.utils.backend_logger import log_path


class BackendLogger:
    def __init__(self):
        caller_frame = inspect.getouterframes(inspect.currentframe())[1]
        time_format = datetime.now().strftime("%Y_%m_%d_%H_%M")
        self.log_file_path = f"{log_path}/{caller_frame.filename.split('/')[-1]}_{time_format}.log"
        # self.log_file_path = f"{log_path}/{os.path.dirname(caller_frame.filename)}/{caller_frame.filename.split('/')[-1]}_{time_format}.log"

    def general_log(self, message):
        caller_frame = inspect.getouterframes(inspect.currentframe())[1]
        caller_file_name = caller_frame.filename.split('/')[-1]

        logger = logging.getLogger(caller_file_name)
        logger.setLevel(logging.DEBUG)


        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s'))
        logger.addHandler(file_handler)


        logger.info(f"{message}   function : {caller_frame.function}:{caller_frame.lineno}\n")
        # if level == 'CRITICAL':
        #     logger.critical(f"{message} at line {caller_frame.lineno} @ {caller_frame.filename}")



