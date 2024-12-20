import os
import json
import requests
# from src.pick_primers import cache_path, output_path
from src.utils.backend_logger.logger import BackendLogger
from src.utils.config_parser.config_parser import parse_config


class GetSequence:
    def __init__(self, chr, coord, flanks):
        self.chr = chr
        self.coord = int(coord)
        self.flanks = int(flanks)
        self.lcoord = self.coord - self.flanks
        self.rcoord = self.coord + self.flanks
        self.config = parse_config('Pick_primers')
        self.cache_path = self.config['cache_path']
        self.logger = BackendLogger()
        self.seq_filename = os.path.join(self.cache_path, f"{self.chr}_{self.coord}.txt")
        # self.get_seq_from_api()

    def get_seq_from_api(self):
        # url = "https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom={self.chr};start={self.lcoord};end={self.rcoord}"

        url = self.config['ucsc_url'].format(self.chr, self.lcoord - 1, self.rcoord)
        self.logger.general_log(f"Requesting sequence using url {url}")
        try:
            resp = requests.get(url)
        except ConnectionError as e:
            return {"error": e}
        self.logger.general_log(f"Response code {resp.status_code}")

        if resp.status_code == 200:
            # dna_char = [char for char in resp.json()['dna'].strip().upper()]
            dna = resp.json()['dna'].strip().upper()

            if not os.path.exists(self.seq_filename):
                with open(self.seq_filename, 'w') as f:
                    f.write(dna)
                    f.close()
                    self.logger.general_log(f"DNA sequence written to file {self.seq_filename}")

            return json.dumps({"dna": dna})
        else:
            return None




# chr1:155295547
# obj = GetSequence('chr1', '155295547', '1000')
# print(obj.get_seq_from_api())
