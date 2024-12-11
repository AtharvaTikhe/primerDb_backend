import re
from src.utils.backend_logger.logger import BackendLogger

def run_regex_medvardb(regex, text):
    matches = re.finditer(regex, text, re.MULTILINE)
    if text == 'N/A':
        return text

    main = ""
    for _, match in enumerate(matches):
        temps = ""
        groups = match.groups()
        #modified_record = f"{groups[0]}\t{groups[1]}\t{groups[2]}\t{match.groups()[-1].split('|')[-1]}\n"
        modified_record = f"{groups[0]}:{int(groups[1])+1}{groups[4]}>{groups[5]}\t{groups[3].split('|')[-1]}\n"
        temps += modified_record
        main += temps

    return main

def run_regex_crdb(regex, text):
    matches = re.finditer(regex, text, re.MULTILINE)
    if text == 'N/A':
        return text

    main = ""

    for _, match in enumerate(matches):
        temps = ""
        groups = match.groups()
        #modified_record = f"{groups[0]}\t{groups[1]}\t{groups[2]}\t{groups[4]}\n"
        modified_record = f"{groups[0]}:{int(groups[1])+1}{groups[4]}>{groups[5]}\t{groups[6]}\n"
        temps += modified_record
        main += temps

    return main

def run_regex_1000G(regex, text):
    matches = re.finditer(regex, text, re.MULTILINE)
    if text == 'N/A':
        return text

    main = ""

    for _, match in enumerate(matches):
        temps = ""
        groups = match.groups()
        #modified_record = f"{groups[0]}\t{groups[1]}\t{groups[2]}\t{groups[3].split('|')[-1]}\n"
        modified_record = f"{groups[0]}:{int(groups[1])+1}{groups[4]}>{groups[5]}\t{groups[7]}\n"
        temps += modified_record
        main += temps

    return main


def run_regex_gnomad(regex, text):
    matches = re.finditer(regex, text, re.MULTILINE)
    if text == 'N/A':
        return text
    else:
        main = ""

    for _, match in enumerate(matches):
        temps = ""
        groups = match.groups()
        # modified_record = f"{groups[0]}\t{groups[1]}\t{groups[3].split(';')[6]}\n"
        # print(groups)
        modified_record = f"{groups[0]}:{groups[1]}{groups[3]}>{groups[4]}\t{groups[8]}\n"
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
        regex = r"^(chr[1-9,XYM]+)\t(\d+)\t(\d+)\t(.*)"
        regex = r"^(chr[1-9,XYM]+)\t(\d+)\t(\d+)\t(\w+\|\w+\|\w+\|(\w+)\|(\w+)*.*)"
        self.result_dict[self.id]['MedVarDb']['forward']['result'] = run_regex_medvardb(regex, self.result_dict[self.id]['MedVarDb']['forward']['result'])
        self.result_dict[self.id]['MedVarDb']['reverse']['result'] = run_regex_medvardb(regex,self.result_dict[self.id]['MedVarDb']['reverse']['result'])

    def _parse_crdb(self):
        regex = r"^(chr[1-9,XYM]+)\t(\d+)\t(\d+)\t(\w:\w:(\w):\w:\w:\w:\w)\t(\d)\t([+-])"
        regex = r"^(chr[1-9,XYM]+)\t(\d+)\s+(\d+)\s+((\w+):(\w+):(\w):\w:\w:\w:\w)\s+(\d+)\s+([+-])"
        # if self.result_dict[self.id]['CRDB']['forward']['result'] != "" and self.result_dict[self.id]['CRDB']['reverse']['result'] != "" :
        self.result_dict[self.id]['CRDB']['forward']['result'] = run_regex_crdb(regex, self.result_dict[self.id]['CRDB']['forward']['result'])
        self.result_dict[self.id]['CRDB']['reverse']['result'] = run_regex_crdb(regex,self.result_dict[self.id]['CRDB']['reverse']['result'])
        # else:
        #     pass

    def _parse_1000G(self):
        regex = r"^(chr[1-9,XYM]+)\t(\d+)\t(\d+)\t(.*)\t(\d)\t([+-])"
        regex = r"^(chr[1-9,XYM]+)\s+(\d+)\s+(\d+)\s+(\w+\|(\w+)\|(\w+)\|(\w+)\|\w+\|\w+\|[\d.]+\|[\d.]+\|[\d.]+\|[\d.]+\|[\d.]+\|([\d.]+))\s+(\d+)\s+([_+])"
        # if self.result_dict[self.id]['1000G']['forward']['result'] != "" and self.result_dict[self.id]['1000G']['reverse']['result'] != "" :
        self.result_dict[self.id]['1000G']['forward']['result'] = run_regex_1000G(regex,self.result_dict[self.id]['1000G']['forward']['result'])
        self.result_dict[self.id]['1000G']['reverse']['result'] = run_regex_1000G(regex,self.result_dict[self.id]['1000G']['reverse']['result'])
        # else:
        #     pass

    def _parse_gnomad(self):
        regex = r"^(chr[1-9,XYM]+)\t(\d+)\t(.+)\t(.*)"
        # regex = r"^(chr[1-9,XYM]+)\s+(\d+)\s+([\w.]+)\t(\w+)\t(\w+)\t([\w.]+)\t([\w.]+)\s+(.+;(AF=[\d.]+))"
        # regex = r"^(chr[1-9,XYM]+)   (\d+)        ([\w.]+)       (\w+)       (\w+)       ([\w.]+)       ([\w.]+)\s+(.+;(AF=[\d.]+))"
        # regex = r"^(chr[1-9,XYM]+)\t(\d+)\t+([\w.]+)\t+(\w+)\t+(\w+)\t+([\w.]+)\t+([\w.]+)\s+(.+;(AF=[\d.]+))"
        regex = r"^(chr[1-9,XYM]+)\t(\d+)\t+([\w.]+)\t+(\w+)\t+(\w+)\t+([\w.]+)\t+([\w.]+)\s+(.+;(AF=[\d.e-]+))"
        self.result_dict[self.id]['gnomad']['forward']['result'] = run_regex_gnomad(regex, self.result_dict[self.id]['gnomad']['forward']['result'])
        self.result_dict[self.id]['gnomad']['reverse']['result'] = run_regex_gnomad(regex,self.result_dict[self.id]['gnomad']['reverse']['result'])

    def parse_results(self):
        self._parse_medvardb()
        self._parse_crdb()
        self._parse_1000G()
        self._parse_gnomad()
        final_res = self.result_dict
        return final_res
