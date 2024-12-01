import json
import os.path
import subprocess
from subprocess import SubprocessError


from src.db_lookup.parse_tabix_output import ParseResults


from src.utils.config_parser.config_parser import parse_config


def run_tabix(db_dict, id):
    for db_name, db_details in db_dict[id].items():

        proc_f = subprocess.run(db_details['cmd'][0], shell=True, capture_output=True, text=True)
        proc_r = subprocess.run(db_details['cmd'][1], shell=True, capture_output=True, text=True)
        if proc_f.returncode == 0 and proc_r.returncode == 0:
            if proc_f.stdout == '':
                db_dict[id][db_name]['forward'] = {'region': db_details['forward'], 'result': 'N/A'}
            else:
                db_dict[id][db_name]['forward'] = {'region': db_details['forward'], 'result': proc_f.stdout}

            if proc_r.stdout == '':
                db_dict[id][db_name]['reverse'] = {'region': db_details['reverse'], 'result': 'N/A'}
            else:
                db_dict[id][db_name]['reverse'] = {'region': db_details['reverse'], 'result': proc_r.stdout}
        else:
            print(f'forward primer process returned : {db_details["cmd"][0]} {proc_f.returncode} {proc_f.stderr}')
            print(f'reverse primer process returned : {db_details["cmd"][1]} {proc_r.returncode} {proc_r.stderr}')

    return db_dict


class DbLookup:

    def __init__(self, positions: dict, id):
        config = parse_config('Db_lookup')
        self.tabix_bin = config['tabix_bin']
        self.db_root = config['db_root']
        self.gnomad_root = config['gnomad_root']
        self.id = id
        self.positions = positions
        # self.generate_results()

    def generate_results(self):
        for key, value in self.positions.items():
            if key == 'error':
                return self.positions

            self.chr = key
            self.forward_primer_range = value['forward_primer']
            self.reverse_primer_range = value['reverse_primer']
            self.prod_range = f"{value['prod_start']}-{value['prod_end']}"

        self.primer_pair = {
            "forward": self.forward_primer_range,
            "reverse": self.reverse_primer_range
        }

        # define database paths
        self.medvar_db = os.path.join(self.db_root, f"{self.chr}.MedVarDb.tsv.gz")
        self.thousand_genomes = os.path.join(self.db_root, f"{self.chr}.1000G.tsv.gz")
        self.gnomad = os.path.join(self.gnomad_root, f"{self.chr}.gnomad.gr38.vcf.gz")

        crdb_path = os.path.join(self.db_root, f"CRDB.{self.chr}.bed.gz")
        if os.path.exists(crdb_path):
            self.crdb = f"{self.db_root}/CRDB.{self.chr}.bed.gz"
        else:
            self.crdb = os.path.join(self.db_root, "CRDB.bed.gz")

        results = run_tabix(self.command_generator(), self.id)
        return results

    def command_generator(self):
        db_dict = {
            "MedVarDb": self.medvar_db,
            "CRDB": self.crdb,
            "1000G": self.thousand_genomes,
            "gnomad": self.gnomad
        }

        """
        dict:
        medvar_db:
        |----------> forward_primer
        |            |-------------> region
        |            |-------------> tabix output
        |-----------> reverse_primer            
                     |-------------> region
                     |-------------> tabix output
        
        """
        self.pre_db_result = {}
        self.pre_db_result[self.id] = {}  # create template, populate dict in run_tabix function.

        for db_name, db_cmd in db_dict.items():
            temp_command = []
            self.pre_db_result[self.id][db_name] = {}

            for primer_name, primer_range in self.primer_pair.items():
                temp_command.append(f"{self.tabix_bin} {db_cmd} {self.chr}:{primer_range}")
                self.pre_db_result[self.id][db_name][primer_name] = primer_range
            self.pre_db_result[self.id][db_name]["cmd"] = temp_command

        return self.pre_db_result

    def parse_results(self):
        results = self.generate_results()
        if 'error' in results.keys():
            return results
        else:
            parser = ParseResults(results, self.id)
            return parser.parse_results()


if __name__ == '__main__':
    from src.pick_primers.run_primer3 import GenerateP3Input
    from src.db_lookup.ucsc_scraper import UCSCScraper

    def get_res(chr, coord, flanks, seq_id, target, num_ret):
        obj = GenerateP3Input(chr, coord, flanks, seq_id, target, num_ret)
        primers, full_output = obj.run_primer3()

        for key, value in primers.items():
            obj = UCSCScraper(f'chr13_{int(key) + 1}', value['left_primer'], value['right_primer'])
            db_obj = DbLookup(obj.get_coords(), f'{int(key) + 1}')
            print(db_obj.parse_results())


    get_res('chr13', "20189511", '1000', 'CHR13x1', '900,200', '1')
    # get_res('chr1', "15529554", '1000', 'CHR1', '900,200', '1')
    # get_res('chr10', "70600902", '1000', 'CHR10', '900,200', '10')
