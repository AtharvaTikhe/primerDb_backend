import json

"""

For Check primer functionality - pass sequence ID and sequences.
The returned string has to be loaded as JSON. The JSON contains DB data as well.

"""
from src.check_primers.check_primer import CheckPrimer
# obj = CheckPrimer("TEST1", "CACACGTTCTTGCAGCCTG", "TCCTGTGTTGTGTGCATTCG")
obj = CheckPrimer("TEST1", "CACACGTTCTTGCAGA", "TCCTGTGTTGTGTGCATTCG")
out = obj.run_primer3()
print(out)

"""

For Pick primer functionality -
`run_primer()` returns two JSONs, primer_pairs and full_output (used only for diagnostics, logging and recording)
primer_pairs JSON now has database results as well.

"""
# from src.pick_primers.run_primer3 import GenerateP3Input
#
# obj = GenerateP3Input('chr1', "15529554", '1000', 'CHR1', '900,200', '2')
#
# primer_pairs, full_output = obj.run_primer3()
# print(primer_pairs)

# from src.utils.Db.dbInteract import CheckEntry
# db_entry = CheckEntry('chr1', "15529554", '1000', 'CHR1', '900,200', '2', primer_pairs)
# print(db_entry.check_entry(add_if_absent=True))
# print(db_entry.query_all())


