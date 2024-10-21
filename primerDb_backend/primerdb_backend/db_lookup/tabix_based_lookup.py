import subprocess

from primerDb_backend.primerdb_backend.db_lookup.ucsc_scraper import UCSCScraper


obj = UCSCScraper('CAMK2','CAGCAGCAGAAGCACACTCAAG','GCAGAAGGAGACAGGTGACCAG')

print(obj.get_coords())
