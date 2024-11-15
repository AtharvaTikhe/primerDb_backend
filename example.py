import json

"""

For Check primer functionality - pass sequence ID and sequences.
The returned string has to be loaded as JSON. The JSON contains DB data as well.

"""
from src.check_primers.check_primer import CheckPrimer
obj = CheckPrimer("TEST1", "CACACGTTCTTGCAGCCTG", "TCCTGTGTTGTGTGCATTCG")
out = json.loads(obj.run_primer3())
print(out)

"""

For Pick primer functionality -
`run_primer()` returns two JSONs, primer_pairs and full_output (used only for diagnostics, logging and recording)
primer_pairs JSON now has database results as well.

"""
from src.pick_primers.run_primer3 import GenerateP3Input
obj = GenerateP3Input('chr1', "15529554", '1000', 'CHR1', '900,200', '5')
primer_pairs, full_output = obj.run_primer3()
print(primer_pairs)
