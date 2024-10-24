import re
import sys
from collections import defaultdict
import pandas as pd

from src.utils.backend_logger.logger import BackendLogger
from src.utils.backend_logger import *

class GetPrimerDetails(BackendLogger):
    """
        This class parses the primer3 output file to return a JSON used for downstream applications.
        The instance will directly be provided a JSON string, all the options for generating JSON (file or string output)
        should be passed during instance creation.

        Attributes:
            p3_file : Input primer3 output file in boulder format
            seq_ret_regex : sequence retrieval regex
            pos_ret_regex : positions retrieval regex

        Returns:
            JSON file/string

    """

    def __init__(self, primer3_out_path, write_json=False):
        super().__init__()
        self.p3_file = primer3_out_path
        self.write_json = write_json

        self._text = self.__get_file_contents()
        self.seq_ret_regex = r"(PRIMER_[L,R]\w+_\d_SEQUENCE)=([ATGC]*)"
        self.pos_ret_regex = r"(PRIMER_[L,R]\w+_\d)=(\d+,\d+)"

        self.__seq_matches = self.__match_with_regex(self.seq_ret_regex)
        self.__sequence_dict = self.__get_seq_dict(self.__seq_matches)

        self.__pos_matches = self.__match_with_regex(self.pos_ret_regex)
        self.__position_dict = self.__get_pos_dict(self.__pos_matches)

        self.json = self.get_primer_details(self.write_json)

        # self.logger = BackendLogger()




    def __get_file_contents(self):
        """
            Read primer3_out file
            Returns:
                  (String) file contents
        """
        with open(self.p3_file, 'r') as f:
            text = " ".join(f.readlines())
        return text


    def __match_with_regex(self, regex):
        """Use `re` module to find given regex in the p3_out file
            Parameters:
                regex (String) : expression to find sequences/positions

            Returns:
                matches (Iterator[Match[str]]) : Iterator returned by finditer
        """
        matches = re.finditer(regex, self._text, re.MULTILINE)

        return matches

    def __get_seq_dict(self, matches):
        """ This function generates a dictionary of L/R primer sequences from the matched regex output

            Parameters:
                matches: Iterator[Match[str]]

            Returns:
                export_dict (dict) : Sequence dictionary containing L/R primer sequences.
        """

        tuple_holder = [] # List containing tuples of matched groups.
        for matchNum, match in enumerate(matches):
            # print(match.groups())
            tuple_holder.append(match.groups())
        super().general_log(f"Matches found {len(tuple_holder)}")
        export_dict = {} # will contain dictionaries of L/R primer sequences

        # INDEXING AND STEP SETTING is based on the shape of the tuple.
        for i in range(0, len(tuple_holder), 2):
            primer_ind = {} # Individual primers
            seq_no = tuple_holder[i][0].split('_')[-2] # Get sequence number. Ex: 0,1,2 etc
            primer_ind[seq_no] = {}

            # L/R exist in pairs; logic works because step size is 2 and there is a pair
            primer_ind[seq_no]['left'] = tuple_holder[i][1]
            primer_ind[seq_no]['right'] = tuple_holder[i + 1][1]
            export_dict.update(primer_ind)

        return export_dict


    def __get_pos_dict(self, matches):
        """ Get primer sequence range (start index & end_index) from the regex match iterator.
            The end position calculation is done from the input primer length given by primer3 (tuple[1][1]).

            Parameters:
                 matches: Iterator returned by re.finditer()
            Returns:
                dict: dictionary collection of `L/R -> start/end position per primer`
        """
        pos_tuple_holder = []
        for _, match in enumerate(matches):

            # print(f"{match.groups()[0]} -- {match.groups()[1].split(',')[0]} to {int(match.groups()[1].split(',')[0]) + int(match.groups()[1].split(',')[1])}")
            pos_tuple_holder.append(match.groups())

        super().general_log(f"Matches found {len(pos_tuple_holder)}")

        primer_pos_total = defaultdict(dict)
        for i in range(0, len(pos_tuple_holder), 2):
            primer_ind = {}
            seq_no = pos_tuple_holder[i][0].split('_')[2]
            temp_left_primer = {'left': {"start": pos_tuple_holder[i][1].split(',')[0],
                                         'end': int(pos_tuple_holder[i][1].split(',')[0]) + int(pos_tuple_holder[i][1].split(',')[1])}}

            temp_right_primer = {'right': {"start": pos_tuple_holder[i + 1][1].split(',')[0],
                                           'end': int(pos_tuple_holder[i + 1][1].split(',')[0]) + int(
                                               pos_tuple_holder[i + 1][1].split(',')[1])}}

            temp_left_primer.update(temp_right_primer)

            primer_ind[seq_no] = temp_left_primer
            primer_pos_total.update(primer_ind)

        return primer_pos_total


    def __merge_primer_dicts(self, sequence_dict, positions_dict, write_json = False):
        """ Take the sequence and positions dictionary and concat to make final json
         with index = sequence number.

         Parameters:
             sequence_dict (dict) : Forward/Reverse primer wise dictionary of sequences
             positions_dict (dict) : Forward/Reverse primer wise dictionary of positions
            write_json (bool) : Boolean to decide if writing the json is required
        Returns:
            merged_json (string) : merged JSON of both dicts

         """
        seq_df = pd.DataFrame(sequence_dict)
        pos_df = pd.DataFrame(positions_dict)

        seq_df = seq_df.T
        pos_df = pos_df.T

        merge = pd.concat([pos_df, seq_df], axis=1)

        merge.columns = ['left_pos', 'right_pos', 'left_primer', 'right_primer']
        merge = merge.T
        super().general_log(f"Merging complete: {merge}")
        if write_json is True:
            merge.to_json(f"{self.p3_file.split('.')[0]}_primers.json")
        return merge.to_json()

    def get_primer_details(self, write_json = False):

        super().general_log(f"writing JSON {self.p3_file.split('.')[0]}_primers.json")

        return self.__merge_primer_dicts(self.__sequence_dict, self.__position_dict, write_json)



if __name__ == "__main__":
    json_out = GetPrimerDetails(sys.argv[1], write_json=True)

    import json
    test = json.loads(json_out.json)
    print(test)

