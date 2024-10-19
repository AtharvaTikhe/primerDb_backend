import json
import re
import os.path
import subprocess
from collections import defaultdict
from subprocess import CalledProcessError
from primerDb_backend.primerdb_backend.utils.backend_logger.logger import BackendLogger
from primerDb_backend.primerdb_backend.utils.primer3_parser.primer3_output_parser import P3outputParser

class CheckPrimer:

    def __init__(self, seq_id, forward, reverse):
        self.seq_id = seq_id
        self.fw = forward
        self.rv = reverse
        self.template = 'template.txt'
        self.out = f'cache/{self.seq_id}.input.txt'
        self.logger = BackendLogger()
        self.primer3_bin = "/home/atharvatikhe/primer_design/primer3-2.6.1/src/primer3_core"
        self._for_rev_files = []


    def __get_seq_data(self):
        return [f'SEQUENCE_ID={self.seq_id}\n', f'SEQUENCE_PRIMER={self.fw}\n', f'SEQUENCE_PRIMER_REVCOMP={self.rv}\n', 'P3_FILE_FLAG=1\n']


    def generate_input(self):
        # Check cache if file exists
        if os.path.exists(self.out):
            self.logger.general_log(f'{self.out} already exists...skipping creation')

            print("file exists already; load results?")# future caching method
            pass
        else:
            with open(self.out, 'w') as f:
                template = open(self.template, 'r').readlines()
                f.writelines(self.__get_seq_data())
                f.writelines(template)
                f.close()

    def run_primer3(self):
        self.generate_input()
        try:
            proc = subprocess.run([f"{self.primer3_bin} {self.out}"], shell = True, capture_output = True, text = True)

            if proc.stderr != '':
                self.logger.general_log(f"primer3 returned {proc.returncode} : {proc.stderr}")
            elif proc.returncode == 0:
                self.logger.general_log(f"primer3 ran successfully for {self.out}")

            with open(f'output/{self.seq_id}.out.txt', 'w') as f:
                f.writelines(proc.stdout)
                f.close()

            os.rename(f"{self.seq_id}.for", f"output/{self.seq_id}.for")
            os.rename(f"{self.seq_id}.rev", f"output/{self.seq_id}.rev")
            self._for_rev_files.append(open(f'output/{self.seq_id}.for', 'r'))
            self._for_rev_files.append(open(f'output/{self.seq_id}.rev', 'r'))

        except CalledProcessError as e:
            self.logger.general_log(f"ERROR RUNNING PRIMER3 : {e}")

        return self.parse_p3_output()


    def parse_p3_output(self):
        fw_content = self._for_rev_files[0].readlines()
        rv_content = self._for_rev_files[1].readlines()

        regex = r"([0-9])\s([ATGC]+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+.\d+)\s*(\d+.\d+)\s*(\d+.\d+)\s*(\d+.\d+)\s*(\d+.\d+)\s*(\d+.\d+)"

        export_dict = defaultdict(dict)

        for _, match in enumerate(re.finditer(regex, fw_content[-1].strip(), re.MULTILINE)):
            groups = match.groups()
            export_dict['forward']['seq'] = groups[1]
            export_dict['forward']['1_based_start'] = groups[2]
            export_dict['forward']['len'] = groups[3]
            export_dict['forward']['num_N'] = groups[4]
            export_dict['forward']['GC'] = groups[5]
            export_dict['forward']['Tm'] = groups[6]
            export_dict['forward']['self_any_th'] = groups[7]
            export_dict['forward']['self_end_th'] = groups[8]
            export_dict['forward']['hairpin'] = groups[9]
            export_dict['forward']['quality'] = groups[10]

        for _, match in enumerate(re.finditer(regex, rv_content[-1].strip(), re.MULTILINE)):
            groups = match.groups()
            export_dict['reverse']['seq'] = groups[1]
            export_dict['reverse']['1_based_start'] = groups[2]
            export_dict['reverse']['len'] = groups[3]
            export_dict['reverse']['num_N'] = groups[4]
            export_dict['reverse']['GC'] = groups[5]
            export_dict['reverse']['Tm'] = groups[6]
            export_dict['reverse']['self_any_th'] = groups[7]
            export_dict['reverse']['self_end_th'] = groups[8]
            export_dict['reverse']['hairpin'] = groups[9]
            export_dict['reverse']['quality'] = groups[10]

        p3_out = P3outputParser(f'output/{self.seq_id}.out.txt')

        with open(f'output/{self.seq_id}.json', 'w', encoding='utf-8') as f:
            json.dump(json.loads(p3_out.parse_file()), f, ensure_ascii=False, indent=4)
            f.close()

        return json.dumps(export_dict)


"""
Example: 

obj = CheckPrimer("CAMK2B", "CAGCAGCAGAAGCACACTCAAG", "GCAGAAGGAGACAGGTGACCAG")
out = obj.run_primer3()

`out` is a json string

"""
