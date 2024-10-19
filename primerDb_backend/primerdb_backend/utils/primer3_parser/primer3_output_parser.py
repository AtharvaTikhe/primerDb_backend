import json
from primerDb_backend.primerdb_backend.utils.backend_logger.logger import BackendLogger

class P3outputParser(BackendLogger):
    def __init__(self, p3_file):
        super().__init__()
        self.file = p3_file
        super().general_log(f"Loading {self.file} for parsing...")

    def parse_file(self):
        with open(self.file, 'r') as f:
            content = f.readlines()
        # ignore lines that do not contain boulder format
        #  structure : key=value (EOF : =)
        content = [line.strip() for line in content if '=' in line]

        super().general_log(f"p3 file contains {len(content)} lines")
        content = [line.split('=') for line in content if line != '=']

        content = [{line[0] : line[1]} for line in content]

        json_string = json.dumps(content)
        super().general_log("file contents converted to JSON successfully!")
        return json_string




"""
Example:
obj = P3outputParser('/path/to/p3_out_file')
obj.parse_file() # returns a json string - read with json.loads()

"""