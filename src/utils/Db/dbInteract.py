import hashlib
from collections import defaultdict

from src.utils.Db.primerDb import InputParameters, PrimerPairs, get_session

def get_hash(input_string):
    return hashlib.md5(input_string.encode()).hexdigest()

class CheckEntry:
    def __init__(self, chr, pos, flanks, seq_id, target, num_ret):
        self.chr = chr
        self.pos = pos
        self.flanks = flanks
        self.seq_id = seq_id
        self.target = target
        self.num_ret = num_ret
        self.input_string = self.chr + self.pos + self.flanks + self.seq_id + self.target + self.num_ret
        self.input_hash = hashlib.md5(self.input_string.encode()).hexdigest()

        self.session = get_session()


    def query_all_input_params(self):
        input_params = self.session.query(InputParameters).all()
        res = []
        for i in range(len(input_params)):
            res.append(input_params[i].__dict__)
        return res

    def check_entry(self):
        hash_check = self.session.query(InputParameters).filter(InputParameters.hash == self.input_hash).all()
        if len(hash_check)  == 1:
            # self.input_params = hash_check[0]
            return 1
            # return self.get_primer_pairs(hash_check[0])
        else:
            return 0

    def get_primer_pairs(self):
        self.input_params = self.session.query(InputParameters).filter(InputParameters.hash == self.input_hash).all()[0]
        primer_pair_data = self.session.query(PrimerPairs).filter(PrimerPairs.input_parameter_id == self.input_params.id).all()
        primer_pair = defaultdict(dict)
        primer_pairs = {}
        for i in range(len(primer_pair_data)):
            pair_dict = primer_pair_data[i].__dict__
            primer_pair[f"{i}"] = {'left_pos': {"start" : pair_dict['left_start_pos'], "end": pair_dict['left_end_pos']}, "right_pos": {"start": pair_dict['right_start_pos'], "end": pair_dict['right_end_pos']}, "left_primer": pair_dict["left_primer"], "right_primer": pair_dict['right_primer'], f"PRIMER_LEFT_{i}_TM": pair_dict['left_tm'], f'PRIMER_RIGHT_{i}_TM': pair_dict['right_tm'], f'PRIMER_LEFT_{i}_GC_PERCENT': pair_dict['left_gc'], f'PRIMER_RIGHT_{i}_GC_PERCENT': pair_dict['right_gc'], "MedVarDb": {"forward": {"result": pair_dict['MedvarDb_forward']}, "reverse": {"result": pair_dict['MedvarDb_reverse']}}, "CRDB" : {"forward": {"result": pair_dict['CRDB_forward']}, "reverse": pair_dict['CRDB_reverse']}, "1000G": {"forward": {"result": pair_dict['thousandG_forward']}, "reverse": pair_dict['thousandG_reverse']}, "gnomAD": {'forward': {'result': pair_dict['gnomad_forward']}, "reverse": pair_dict['gnomad_reverse']}, "left_coords": {"start": pair_dict['left_cord_start'], "end": pair_dict['left_cord_end']}, "right_coords": {"start": pair_dict['right_cord_start'], "end": pair_dict['right_cord_end']}}
            primer_pairs.update(primer_pair)

        return primer_pairs


    def add_entry(self, pairs):
        input_params = InputParameters(seq_id=self.seq_id, chr=self.chr, variant_pos=self.pos, target=self.target,flanks= self.flanks, num_ret=self.num_ret, hash = self.input_hash)
        self.session.add(input_params)
        self.session.commit()

        for key in pairs.keys():
            pair = pairs[key]
            db_pair = PrimerPairs(left_start_pos=pair['left_pos']['start'], left_end_pos=pair['left_pos']['end'],
                                  right_start_pos=pair['right_pos']['start'], right_end_pos=pair['right_pos']['end'],
                                  left_primer=pair['left_primer'], right_primer=pair['right_primer'],
                                  left_tm=pair[f'PRIMER_LEFT_{key}_TM'], left_gc=pair[f'PRIMER_LEFT_{key}_GC_PERCENT'],
                                  right_tm=pair[f'PRIMER_RIGHT_{key}_TM'],
                                  right_gc=pair[f'PRIMER_RIGHT_{key}_GC_PERCENT'],
                                  MedvarDb_forward=pair['MedVarDb']['forward']['result'],
                                  MedvarDb_reverse=pair['MedVarDb']['reverse']['result'],
                                  thousandG_forward=pair['1000G']['forward']['result'],
                                  thousandG_reverse=pair['1000G']['reverse']['result'],
                                  CRDB_forward=pair['CRDB']['forward']['result'],
                                  CRDB_reverse=pair['CRDB']['reverse']['result'],
                                  gnomad_forward=pair['gnomad']['forward']['result'],
                                  gnomad_reverse=pair['gnomad']['reverse']['result'],
                                  left_cord_start=pair['left_coords']['start'],
                                  left_cord_end=pair['left_coords']['end'],
                                  right_cord_start=pair['right_coords']['start'],
                                  right_cord_end=pair['right_coords']['end'], input_parameter_id = input_params.id)
            self.session.add(db_pair)
            self.session.commit()


# CheckEntry('chr1', "15529554", '1000', 'CHR1', '900,200', '5')

