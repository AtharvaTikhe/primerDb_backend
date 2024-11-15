import configparser
def parse_config(category):
    config = configparser.ConfigParser()
    config.read('/home/atharvatikhe/primerDb_backend/src/config.ini')
    config_values = {}
    try:
        if category == 'Pick_primers':
            config_values['cache_path'] = config.get(category, 'cache_path')
            config_values['output_path'] = config.get(category, 'output_path')
            config_values['primer3_bin'] = config.get(category, 'primer3_bin')
            config_values['primer3_settings'] = config.get(category, 'primer3_settings')
        if category == 'Db_lookup':
            config_values['tabix_bin'] = config.get(category, 'tabix_bin')
            config_values['db_root'] = config.get(category, 'db_root')
        if category == 'logger':
            config_values['log_path'] = config.get(category, 'log_path')
        if category == 'Check_primers':
            config_values['cache_path'] = config.get(category, 'cache_path')
            config_values['output_path'] = config.get(category, 'output_path')
            config_values['primer3_bin'] = config.get(category, 'primer3_bin')
    except configparser.NoOptionError:
        print(category)

    return config_values
