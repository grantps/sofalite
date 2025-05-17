"""
Remember sofalite.conf CUSTOM_DBS_FOLDER
"""

from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML(typ='safe')  ## default, if not specified, is 'rt' (round-trip)

def run():
    yaml_fpath = Path('/home/g/projects/sofalite/store/sqlite.yaml')
    raw_yaml = yaml.load(yaml_fpath)
    print(raw_yaml)

if __name__ == '__main__':
    run()
