import json
import subprocess

from primerDb_backend.primerdb_backend.db_lookup.ucsc_scraper import UCSCScraper

class DbLookup:
    def __init__(self, positions: dict):

        for key, value in positions.items():
            self.chr = key
            # print(value)
            self.forward_primer_range = value['forward_primer']
            self.reverse_primer_range = value['reverse_primer']

        print(self.chr)
        print(self.forward_primer_range)
        print(self.reverse_primer_range)



"""
/MGMSTAR1/SHARED/RESOURCES/APPS/htslib-1.2.1/bin/tabix /MGMSTAR15/SHARED/RESOURCES/VariMAT/VariMAT_RESOURCES/VARIMAT2.5.2/GR38_RESOURCES/chr1.MedVarDb.tsv.gz chr1:13118-13128
"""
obj = UCSCScraper('CAMK2','CAGCAGCAGAAGCACACTCAAG','GCAGAAGGAGACAGGTGACCAG')

db_obj = DbLookup(obj.get_coords())

print(obj.get_coords())
