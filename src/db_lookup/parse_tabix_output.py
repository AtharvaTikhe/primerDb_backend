import string

from src.utils.backend_logger.logger import BackendLogger

class ParseResults:
    def __init__(self, result_dict: dict, id):
        self.log = BackendLogger()
        self.result_dict = result_dict
        self.id = id
        self.parse_results()

    def parse_medvardb(result):


    def parse_results(self):
        self.db_details = self.result_dict[self.id]
        self.db_details['MedVarDb']

