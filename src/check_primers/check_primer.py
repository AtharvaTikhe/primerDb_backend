import json
import re
import os.path
import subprocess
from collections import defaultdict
from subprocess import CalledProcessError

from src.db_lookup.tabix_based_lookup import DbLookup
from src.db_lookup.ucsc_scraper import UCSCScraper
from src.utils.backend_logger.logger import BackendLogger
from src.utils.primer3_parser.primer3_output_parser import P3outputParser
from src.utils.config_parser.config_parser import parse_config


class CheckPrimer:

    def __init__(self, seq_id, forward, reverse, p_size_min = 15, p_size_opt = 21, p_size_max = 26, p_temp_min = 45, p_temp_opt = 55, p_temp_max = 75, p_gc_min = 40, p_gc_opt = 47, p_gc_max = 60, p_prod_size = '27401-27475 30-300 301-400 401-500 501-600 601-700 701-850 851-1000'   ):
        self.seq_id = seq_id
        self.fw = forward
        self.rv = reverse
        self.p_size_min = p_size_min
        self.p_size_opt = p_size_opt
        self.p_size_max = p_size_max
        self.p_temp_min = p_temp_min
        self.p_temp_opt = p_temp_opt
        self.p_temp_max = p_temp_max
        self.p_gc_min = p_gc_min
        self.p_gc_opt = p_gc_opt
        self.p_gc_max = p_gc_max
        self.p_prod_size = p_prod_size.strip()

        self.template = 'src/check_primers/template.txt'

        config = parse_config('Check_primers')

        self.cache_path = config['cache_path']
        self.primer3_bin = config['primer3_bin']
        self.output_path = config['output_path']

        self.out = f'{self.cache_path}/{self.seq_id}.input.txt'
        self.logger = BackendLogger()

        
        self._for_rev_files = []


    def __get_seq_data(self):
        return [f"SEQUENCE_ID={self.seq_id}\n",
                f"SEQUENCE_PRIMER={self.fw}\n",
                f"SEQUENCE_PRIMER_REVCOMP={self.rv}\n",
                "P3_FILE_FLAG=1\n",
                f"PRIMER_MIN_SIZE={self.p_size_min}\n",
                f"PRIMER_OPT_SIZE={self.p_size_opt}\n",
                f"PRIMER_MAX_SIZE={self.p_size_opt}\n",
                f"PRIMER_MIN_TM={self.p_temp_min}\n",
                f"PRIMER_OPT_TM={self.p_temp_opt}\n",
                f"PRIMER_MAX_TM={self.p_temp_max}\n",
                f"PRIMER_MIN_GC={self.p_gc_min}\n",
                f"PRIMER_OPT_GC_PERCENT={self.p_gc_opt}\n",
                f"PRIMER_MAX_GC={self.p_gc_max}\n",
                f"PRIMER_PRODUCT_SIZE_RANGE={self.p_prod_size}\n"]

        # return [f'SEQUENCE_ID={self.seq_id}\n', f'SEQUENCE_PRIMER={self.fw}\n', f'SEQUENCE_PRIMER_REVCOMP={self.rv}\n', 'P3_FILE_FLAG=1\n', '']

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

            with open(f'{self.output_path}/{self.seq_id}.out.txt', 'w') as f:
                f.writelines(proc.stdout)
                f.close()

            if os.path.exists(f"{self.seq_id}.for") and os.path.exists(f"{self.seq_id}.rev"):
                os.rename(f"{self.seq_id}.for", f"{self.output_path}/{self.seq_id}.for")
                os.rename(f"{self.seq_id}.rev", f"{self.output_path}/{self.seq_id}.rev")
                self._for_rev_files.append(open(f'{self.output_path}/{self.seq_id}.for', 'r'))
                self._for_rev_files.append(open(f'{self.output_path}/{self.seq_id}.rev', 'r'))
            else:
                self.logger.general_log(f"NO PRIMERS FOUND! {self.seq_id}")
                os.remove(self.out)

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

        p3_out = P3outputParser(f'{self.output_path}/{self.seq_id}.out.txt')

        with open(f'{self.output_path}/{self.seq_id}.json', 'w', encoding='utf-8') as f:
            json.dump(json.loads(p3_out.parse_file()), f, ensure_ascii=False, indent=4)
            f.close()


        obj = UCSCScraper(self.seq_id, export_dict['forward']['seq'], export_dict['reverse']['seq'])
        db_obj = DbLookup(obj.get_coords(), self.seq_id)
        results = db_obj.parse_results()
        export_dict.update(results[self.seq_id])

        return json.dumps(export_dict)


"""
Example: 

obj = CheckPrimer("CAMK2B", "CAGCAGCAGAAGCACACTCAAG", "GCAGAAGGAGACAGGTGACCAG")
out = obj.run_primer3()

`out` is a json string

"""

if __name__ == "__main__":
    obj = CheckPrimer("TEST1", "CACACGTTCTTGCAGCCTG", "TCCTGTGTTGTGTGCATTCG")
    out = obj.run_primer3()
    print(out)
