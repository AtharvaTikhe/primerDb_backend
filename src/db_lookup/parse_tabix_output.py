import re
from src.utils.backend_logger.logger import BackendLogger

def run_regex_medvardb(regex, text):
    matches = re.finditer(regex, text, re.MULTILINE)

    main = ""
    for _, match in enumerate(matches):
        temps = ""
        groups = match.groups()
        modified_record = f"{groups[0]}\t{groups[1]}\t{groups[2]}\t{match.groups()[-1].split('|')[-1]}\n"
        temps += modified_record
        main += temps

    return main

def run_regex_crdb(regex, text):
    matches = re.finditer(regex, text, re.MULTILINE)
    main = ""

    for _, match in enumerate(matches):
        temps = ""
        groups = match.groups()
        modified_record = f"{groups[0]}\t{groups[1]}\t{groups[2]}\t{groups[4]}\n"
        temps += modified_record
        main += temps

    return main

def run_regex_1000G(regex, text):
    matches = re.finditer(regex, text, re.MULTILINE)
    main = ""

    for _, match in enumerate(matches):
        temps = ""
        groups = match.groups()
        modified_record = f"{groups[0]}\t{groups[1]}\t{groups[2]}\t{groups[3].split('|')[-1]}\n"
        temps += modified_record
        main += temps

    return main


def run_regex_gnomad(regex, text):
    matches = re.finditer(regex, text, re.MULTILINE)
    main = ""

    for _, match in enumerate(matches):
        temps = ""
        groups = match.groups()
        modified_record = f"{groups[0]}\t{groups[1]}\t{groups[3].split(';')[6]}\n"
        temps += modified_record
        main += temps

    return main

class ParseResults:
    def __init__(self, result_dict: dict, id):
        self.log = BackendLogger()

        self.result_dict = result_dict
        self.id = id
        # self.parse_results()


    def _parse_medvardb(self):
        regex = r"^(chr\d+)\t(\d+)\t(\d+)\t(.*)"
        self.result_dict[self.id]['MedVarDb']['forward']['result'] = run_regex_medvardb(regex, self.result_dict[self.id]['MedVarDb']['forward']['result'])
        self.result_dict[self.id]['MedVarDb']['reverse']['result'] = run_regex_medvardb(regex,self.result_dict[self.id]['MedVarDb']['reverse']['result'])

    def _parse_crdb(self):
        regex = r"^(chr\d+)\t(\d+)\t(\d+)\t(\w:\w:(\w):\w:\w:\w:\w)\t(\d)\t([+-])"

        # if self.result_dict[self.id]['CRDB']['forward']['result'] != "" and self.result_dict[self.id]['CRDB']['reverse']['result'] != "" :
        self.result_dict[self.id]['CRDB']['forward']['result'] = run_regex_crdb(regex, self.result_dict[self.id]['CRDB']['forward']['result'])
        self.result_dict[self.id]['CRDB']['reverse']['result'] = run_regex_crdb(regex,self.result_dict[self.id]['CRDB']['reverse']['result'])
        # else:
        #     pass

    def _parse_1000G(self):
        regex = r"^(chr\d+)\t(\d+)\t(\d+)\t(.*)\t(\d)\t([+-])"

        # if self.result_dict[self.id]['1000G']['forward']['result'] != "" and self.result_dict[self.id]['1000G']['reverse']['result'] != "" :
        self.result_dict[self.id]['1000G']['forward']['result'] = run_regex_1000G(regex,self.result_dict[self.id]['1000G']['forward']['result'])
        self.result_dict[self.id]['1000G']['reverse']['result'] = run_regex_1000G(regex,self.result_dict[self.id]['1000G']['reverse']['result'])
        # else:
        #     pass

    def _parse_gnomad(self):
        regex = r"^(chr\d+)\t(\d+)\t(.+)\t(.*)"
        self.result_dict[self.id]['gnomad']['forward']['result'] = run_regex_gnomad(regex, self.result_dict[self.id]['gnomad']['forward']['result'])
        self.result_dict[self.id]['gnomad']['reverse']['result'] = run_regex_gnomad(regex,self.result_dict[self.id]['gnomad']['reverse']['result'])

    def parse_results(self):
        self._parse_medvardb()
        self._parse_crdb()
        self._parse_1000G()
        self._parse_gnomad()
        final_res = self.result_dict
        return final_res
