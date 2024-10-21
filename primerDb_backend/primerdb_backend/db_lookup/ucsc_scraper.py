import requests
import subprocess
from bs4 import BeautifulSoup
import pandas as pd
import re


class UCSCScraper:
    def __init__(self, seq_id, forward, reverse):
        self.seq_id = seq_id
        self.forward = forward
        self.reverse = reverse
        self.url = f"https://genome.ucsc.edu/cgi-bin/hgPcr?hgsid=2362139469_NeGwKF4WE8Mbshi7T4qRFX31fKaE&org=Human&db=hg38&wp_target=genome&wp_f={self.forward}&wp_r={self.reverse}&Submit=Submit&wp_size=8000&wp_perfect=15&wp_good=15&boolshad.wp_flipReverse=0&wp_append=on&boolshad.wp_append=0"
        self.regex = r"^>\w+:\w+\+\w+"



    def get_coords(self):
        try:
            resp = requests.get(self.url)

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                table = soup.find_all('table')[0]
                text = table.get_text()
                matches = re.finditer(self.regex, text, re.MULTILINE)

                coords_string = ""
                for _, match in enumerate(matches, start=1):
                    coords_string = match.group()

                regex = r">(chr\w+):([1-9]+)\+([1-9]+)"
                """ 
                REGEX EXPLANATION
                ^ asserts position at start of a line
                > matches the character > with index 6210 (3E16 or 768) literally (case sensitive)
                \\w matches any word character (equivalent to [a-zA-Z0-9_])
                + matches the previous token between one and unlimited times, as many times as possible, giving back as needed (greedy)
                : matches the character : with index 5810 (3A16 or 728) literally (case sensitive)
                \w matches any word character (equivalent to [a-zA-Z0-9_])
                + matches the previous token between one and unlimited times, as many times as possible, giving back as needed (greedy)
                \+ matches the character + with index 4310 (2B16 or 538) literally (case sensitive)
                \w matches any word character (equivalent to [a-zA-Z0-9_])
                + matches the previous token between one and unlimited times, as many times as possible, giving back as needed (greedy)
    
                """

                matches = re.finditer(regex, coords_string, re.MULTILINE)

                groups = [[group for group in match.groups()] for _, match in enumerate(matches)]
                groups = groups[0]
                export_dict = {
                    groups[0]: {"prod_start": groups[1], "prod_end": groups[2], "forward_primer": f"{groups[1]}-{int(groups[1]) + len(self.forward)}", "reverse_primer": f"{int(groups[2])-len(self.reverse)}-{groups[2]}"}}
                return export_dict
            else:
                raise ConnectionError
        except ConnectionError as e:
            print(e)
            # pass





class DbLookup:
    def __init__(self, positions: dict):

        for key, value in positions.items():
            self.chr = key
            self.forward_primer_range = value['forward_primer']
            self.reverse_primer_range = value['reverse_primer']
            self.prod_range = f"{value['prod_start']}-{value['prod_end']}"

        print(self.chr)
        print(self.forward_primer_range)
        print(self.reverse_primer_range)		
        
        self.command_f = f"/MGMSTAR1/SHARED/RESOURCES/APPS/htslib-1.2.1/bin/tabix /MGMSTAR15/SHARED/RESOURCES/VariMAT/VariMAT_RESOURCES/VARIMAT2.5.2/GR38_RESOURCES/{self.chr}.MedVarDb.tsv.gz {self.chr}:{self.forward_primer_range}"
	
        self.command_r = f"/MGMSTAR1/SHARED/RESOURCES/APPS/htslib-1.2.1/bin/tabix /MGMSTAR15/SHARED/RESOURCES/VariMAT/VariMAT_RESOURCES/VARIMAT2.5.2/GR38_RESOURCES/{self.chr}.MedVarDb.tsv.gz {self.chr}:{self.reverse_primer_range}"
        
        self.command_p = f"/MGMSTAR1/SHARED/RESOURCES/APPS/htslib-1.2.1/bin/tabix /MGMSTAR15/SHARED/RESOURCES/VariMAT/VariMAT_RESOURCES/VARIMAT2.5.2/GR38_RESOURCES/{self.chr}.MedVarDb.tsv.gz {self.chr}:{self.prod_range}"
		
        self.run_tabix(self.command_f)
        self.run_tabix(self.command_r)		
#        self.run_tabix(self.command_p)		
        print(self.command_r)
    def run_tabix(self, command):
        proc = subprocess.run(command, shell = True)

        print(proc.stdout)
        print(proc.stderr)
        print(proc.returncode)



obj = UCSCScraper('CAMK2','CAGCAGCAGAAGCACACTCAAG','GCAGAAGGAGACAGGTGACCAG')


db_obj = DbLookup(obj.get_coords())

print(obj.get_coords())
