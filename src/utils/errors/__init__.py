class InvalidConfigError(Exception):
    def __init__(self):
        self.message = "Can't read config file correctly. (check config path in src/utils/config_parser/config_parser.py)"
        super().__init__(self.message)

