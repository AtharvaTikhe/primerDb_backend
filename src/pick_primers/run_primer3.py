from collections import defaultdict
import json
import os.path
import subprocess
from subprocess import CalledProcessError


from src.db_lookup.tabix_based_lookup import DbLookup
from src.db_lookup.ucsc_scraper import UCSCScraper
from src.utils.primer3_parser.primer3_output_parser import P3outputParser
from src.utils.backend_logger.logger import BackendLogger
from src.utils.config_parser.config_parser import parse_config

# from src.pick_primers import primer3_bin, self.cache_path, self.output_path, primer3_settings
from src.pick_primers.get_primer_seqs import GetPrimerDetails
from src.pick_primers.get_sequence import GetSequence

def get_primer_pair_coords(variant_coord, primer_l_start, primer_l_end, flank, primer_r_end, primer_r_start):
  # primer_r_start = primer_r_end - primer_r_len
  primer_ls_coord = variant_coord - flank + primer_l_start
  # primer_le_coord = variant_coord - flank + primer_l_end - 1
  primer_le_coord = variant_coord - flank + primer_l_end

  # primer_ls_coord, primer_le_coord

  primer_rs_coord = variant_coord - flank + primer_r_end
  primer_re_coord = variant_coord - flank + primer_r_start
  # primer_re_coord = variant_coord - flank + primer_r_start - 1

  # primer_rs_coord, primer_re_coord

  return {'left_coords': {"start": primer_ls_coord, "end" : primer_le_coord}, 'right_coords': {"start": primer_re_coord, "end" : primer_rs_coord }}


class GenerateP3Input:
    def __init__(self, chr, coord, flanks, seq_id, target, num_ret):
        self.chr = chr
        self.coord = coord
        self.flanks = flanks

        config = parse_config('Pick_primers')
        
        self.primer3_bin = config['primer3_bin']
        self.cache_path = config['cache_path']
        self.output_path = config['output_path']
        self.primer3_settings = config['primer3_settings']

        self.seq_id = seq_id

        if len(target.split(',')) == 2:
            self.target = target
        else:
            # assert "Target should have two comma separated values example: 900,200"
            raise ValueError

        self.num_ret = num_ret

        seq = GetSequence(chr, coord, flanks)
        sequence = seq.get_seq_from_api()
        if sequence is not None:
            self.seq = json.loads(sequence)['dna'].strip()
            self.api_error_flag = 0
        else:
            # raise Exception('No Sequence found for given co-ordinates and flanks')
            self.api_error_flag = 1

        self.p3_input_file = os.path.join(self.cache_path, f"{self.seq_id}.{self.num_ret}.input.txt")
        self.p3_output = os.path.join(self.output_path, f"{self.seq_id}.{self.num_ret}.out.txt")
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
        if self.api_error_flag == 1:
            return {'error': 'API Error: Sequence not returned'}, 0


        self.generate_input()
        self.logger.general_log(f"Using primer3 bin : {self.primer3_bin}")
        try:

            proc = subprocess.run([f'{self.primer3_bin} --p3_settings_file="{self.primer3_settings}" --output={self.p3_output} --error="{self.cache_path}/{self.seq_id}_err.txt" {self.p3_input_file} '], shell=True, capture_output=True, text=True)

            if proc.stderr != '' or proc.returncode != 0:
                self.logger.general_log(f"primer3 returned {proc.returncode} : {proc.stderr}")
            elif proc.returncode == 0:
                self.logger.general_log(f"primer3 ran successfully for {self.p3_input_file}")

                # parse output to get primer details as JSON
                primer_seq = GetPrimerDetails(f"{self.p3_output}", True)

                # parse entire output and store as JSON
                parsed_out = P3outputParser(f"{self.p3_output}")

                with open(f"{self.output_path}/{self.seq_id}_p3_out.json", 'w', encoding='utf-8') as f:
                    json.dump(json.loads(parsed_out.parse_file()), f, ensure_ascii=False, indent=4)

                full_output = json.loads(parsed_out.parse_file())
                primer_pairs = json.loads(primer_seq.json)

                main = defaultdict(dict)
                for kv_pair in full_output:
                    for i in range(0, int(self.num_ret)):
                        if f"PRIMER_LEFT_{i}_TM" in kv_pair.keys():
                            main[str(i)].update(kv_pair)
                        if f"PRIMER_RIGHT_{i}_TM" in kv_pair.keys():
                            main[str(i)].update(kv_pair)
                        if f"PRIMER_LEFT_{i}_GC_PERCENT" in kv_pair.keys():
                            main[str(i)].update(kv_pair)
                        if f"PRIMER_RIGHT_{i}_GC_PERCENT" in kv_pair.keys():
                            main[str(i)].update(kv_pair)

                for key in primer_pairs.keys():
                    primer_pairs[key].update(main[key])

                for key in primer_pairs.keys():
                    # Get db results
                    try:
                        obj = UCSCScraper(self.seq_id, primer_pairs[key]['left_primer'], primer_pairs[key]['right_primer'])
                        db_obj = DbLookup(obj.get_coords(), self.seq_id)
                        results = db_obj.parse_results()
                        primer_pairs[key].update(results[self.seq_id])
                    except Exception:
                        return {"error": "DB lookup error; check variant location."}, 0
                    # Get genomic co-ordinates

                    coords = get_primer_pair_coords(int(self.coord), int(primer_pairs[key]['left_pos']['start']), int(primer_pairs[key]['left_pos']['end']), int(self.flanks), int(primer_pairs[key]['right_pos']['end']), int(primer_pairs[key]['right_pos']['start']) )

                    # coords = get_primer_pair_coords(int(self.coord), int(primer_pairs[key]['left_pos']['start']),
                    #                                 int(primer_pairs[key]['left_pos']['end']), int(self.flanks),
                    #                                 int(primer_pairs[key]['right_pos']['end']),
                    #                                 int(primer_pairs[key]['right_pos']['start']))

                    primer_pairs[key].update(coords)

                # get_primer_pair_coords(15529554, 850, 870, 1000, 1243, 1224)



                return primer_pairs, full_output
                # print(json.loads(primer_seq.json))
        except Exception:
            return {"error": "primer3 failed; check input parameters."}, 0
            # self.logger.general_log(f'primer3 failed for {self.p3_input_file}')

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
