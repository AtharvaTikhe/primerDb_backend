import json
import os.path
import subprocess
from subprocess import CalledProcessError

from src.db_lookup.tabix_based_lookup import DbLookup
from src.db_lookup.ucsc_scraper import UCSCScraper
from src.utils.primer3_parser.primer3_output_parser import P3outputParser
from src.utils.backend_logger.logger import BackendLogger

from src.pick_primers import primer3_bin, cache_path, output_path, primer3_settings
from src.pick_primers.get_primer_seqs import GetPrimerDetails
from src.pick_primers.get_sequence import GetSequence



class GenerateP3Input:
    def __init__(self, chr, coord, flanks, seq_id, target, num_ret):
        self.seq_id = seq_id

        if len(target.split(',')) == 2:
            self.target = target
        else:
            # assert "Target should have two comma separated values example: 900,200"
            raise ValueError

        self.num_ret = num_ret

        seq = GetSequence(chr, coord, flanks)
        self.seq = json.loads(seq.get_seq_from_api())['dna'].strip()

        self.p3_input_file = f"{cache_path}/{self.seq_id}.{self.num_ret}.input.txt"
        self.p3_output = f"{output_path}/{self.seq_id}_{self.num_ret}_out.txt"
        self.logger = BackendLogger()


    def generate_input(self):
        # echo "SEQUENCE_ID=${SEQ_ID}"
        # echo "SEQUENCE_TEMPLATE=${SEQ}"
        # echo "SEQUENCE_TARGET=${TARGET}"
        #
        # echo "PRIMER_PICK_LEFT_PRIMER=1"
        # echo "PRIMER_PICK_RIGHT_PRIMER=1"
        # echo "PRIMER_EXPLAIN_FLAG=1"
        # echo "PRIMER_NUM_RETURN=${NUM_RET}"
        # echo "="

        input = [f"SEQUENCE_ID={self.seq_id}", f"SEQUENCE_TEMPLATE={self.seq}", f"SEQUENCE_TARGET={self.target}", f'PRIMER_PICK_LEFT_PRIMER=1', 'PRIMER_PICK_RIGHT_PRIMER=1', "PRIMER_EXPLAIN_FLAG=1", f"PRIMER_NUM_RETURN={self.num_ret}", "="]



        if not os.path.exists(self.p3_input_file):
            with open(self.p3_input_file, 'w') as f:
                f.writelines([item + '\n' for item in input])
                f.close()
            return True
        else:
            self.logger.general_log(f"Input file exists : {self.p3_input_file} ... skipping generation ...")

    def run_primer3(self):
        self.generate_input()
        self.logger.general_log(f"Using primer3 bin : {primer3_bin}")
        try:

            proc = subprocess.run([f'{primer3_bin} --p3_settings_file="{primer3_settings}" --output={self.p3_output} --error="{cache_path}/{self.seq_id}_err.txt" {self.p3_input_file} '], shell=True, capture_output=True, text=True)

            if proc.stderr != '' or proc.returncode != 0:
                self.logger.general_log(f"primer3 returned {proc.returncode} : {proc.stderr}")
            elif proc.returncode == 0:
                self.logger.general_log(f"primer3 ran successfully for {self.p3_input_file}")

                # parse output to get primer details as JSON
                primer_seq = GetPrimerDetails(f"{self.p3_output}", True)

                # parse entire output and store as JSON
                parsed_out = P3outputParser(f"{self.p3_output}")

                with open(f"{output_path}/{self.seq_id}_p3_out.json", 'w') as f:
                    json.dump(json.loads(parsed_out.parse_file()), f, ensure_ascii=False, indent=4)

                return json.loads(primer_seq.json), json.loads(parsed_out.parse_file())
                # print(json.loads(primer_seq.json))
        except CalledProcessError:
            self.logger.general_log(f'primer3 failed for {self.p3_input_file}')

if __name__=="__main__":
    chr = 'chr13'
    obj = GenerateP3Input(chr, '20189511', '1000', 'CHR13', '900,200', '1')
    primer_pairs, full_output = obj.run_primer3()

    print(primer_pairs)
    for key, value in primer_pairs.items():
        obj = UCSCScraper(f'{chr}_{int(key)}', value['left_primer'], value['right_primer'])
        db_obj = DbLookup(obj.get_coords(), f'{int(key)}')
        print(key)
        print('--------------------------')
        print(db_obj.results)
        print(db_obj.parse_results())
