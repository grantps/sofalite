from dataclasses import dataclass
from enum import StrEnum
import os
from pathlib import Path
import platform
from subprocess import Popen, PIPE
from typing import Literal

from sofalite.conf.var_labels import yaml2varlabels

SOFALITE_WEB_RESOURCES_ROOT = 'http://www.sofastatistics.com/sofalite'
# SOFALITE_WEB_RESOURCES_ROOT = 'file:///home/g/projects/sofalite/src/sofalite/output/js'  ## local development - note tooltips won't work because the pngs aren't in the same place in dev as in prod - don't worry about that
SOFALITE_FS_RESOURCES_ROOT = Path('/home/g/Documents/sofalite/reports/report_extras')

MAX_CHI_SQUARE_CELLS = 200  ## was 25
MAX_CHI_SQUARE_VALS_IN_DIM = 30  ## was 6
MIN_CHI_SQUARE_VALS_IN_DIM = 2
MAX_RANK_DATA_VALS = 100_000
MAX_VALUE_LENGTH_IN_SQL_CLAUSE = 90

AVG_LINE_HEIGHT_PIXELS = 12
AVG_CHAR_WIDTH_PIXELS = 20
HISTO_AVG_CHAR_WIDTH_PIXELS = 10.5
DOJO_Y_AXIS_TITLE_OFFSET = 45
TEXT_WIDTH_WHEN_ROTATED = 4
MIN_CHART_WIDTH_PIXELS = 450
MAX_SAFE_X_LBL_LEN_PIXELS = 180

JS_BOOL = Literal['true', 'false']

DOJO_COLOURS = ['indigo', 'gold', 'hotpink', 'firebrick', 'indianred',
    'mistyrose', 'darkolivegreen', 'darkseagreen', 'slategrey', 'tomato',
    'lightcoral', 'orangered', 'navajowhite', 'slategray', 'palegreen',
    'darkslategrey', 'greenyellow', 'burlywood', 'seashell',
    'mediumspringgreen', 'mediumorchid', 'papayawhip', 'blanchedalmond',
    'chartreuse', 'dimgray', 'lemonchiffon', 'peachpuff', 'springgreen',
    'aquamarine', 'orange', 'lightsalmon', 'darkslategray', 'brown', 'ivory',
    'dodgerblue', 'peru', 'lawngreen', 'chocolate', 'crimson', 'forestgreen',
    'darkgrey', 'lightseagreen', 'cyan', 'mintcream', 'transparent',
    'antiquewhite', 'skyblue', 'sienna', 'darkturquoise', 'goldenrod',
    'darkgreen', 'floralwhite', 'darkviolet', 'darkgray', 'moccasin',
    'saddlebrown', 'grey', 'darkslateblue', 'lightskyblue', 'lightpink',
    'mediumvioletred', 'deeppink', 'limegreen', 'darkmagenta', 'palegoldenrod',
    'plum', 'turquoise', 'lightgoldenrodyellow', 'darkgoldenrod', 'lavender',
    'slateblue', 'yellowgreen', 'sandybrown', 'thistle', 'violet', 'magenta',
    'dimgrey', 'tan', 'rosybrown', 'olivedrab', 'pink', 'lightblue',
    'ghostwhite', 'honeydew', 'cornflowerblue', 'linen', 'darkblue',
    'powderblue', 'seagreen', 'darkkhaki', 'snow', 'mediumblue', 'royalblue',
    'lightcyan', 'mediumpurple', 'midnightblue', 'cornsilk', 'paleturquoise',
    'bisque', 'darkcyan', 'khaki', 'wheat', 'darkorchid', 'deepskyblue',
    'salmon', 'darkred', 'steelblue', 'palevioletred', 'lightslategray',
    'aliceblue', 'lightslategrey', 'lightgreen', 'orchid', 'gainsboro',
    'mediumseagreen', 'lightgray', 'mediumturquoise', 'cadetblue',
    'lightyellow', 'lavenderblush', 'coral', 'lightgrey', 'whitesmoke',
    'mediumslateblue', 'darkorange', 'mediumaquamarine', 'darksalmon', 'beige',
    'blueviolet', 'azure', 'lightsteelblue', 'oldlace']

class Platform(StrEnum):
    LINUX = 'linux'
    WINDOWS = 'windows'
    MAC = 'mac'

PLATFORMS = {'Linux': Platform.LINUX, 'Windows': Platform.WINDOWS, 'Darwin': Platform.MAC}
PLATFORM = PLATFORMS.get(platform.system())

def get_local_folder(my_platform: Platform) -> Path:
    home_path = Path(os.path.expanduser('~'))
    if my_platform == Platform.LINUX:  ## see https://bugs.launchpad.net/sofastatistics/+bug/952077
        try:
            user_path = Path(str(Popen(['xdg-user-dir', 'DOCUMENTS'],
                stdout=PIPE).communicate()[0], encoding='utf-8').strip())  ## get output i.e. [0]. err is 2nd.
        except OSError:
            user_path = home_path
    else:
        user_path = home_path
    local_path = user_path / 'sofalite'
    return local_path

LOCAL_FOLDER = get_local_folder(PLATFORM)
INTERNAL_FOLDER = LOCAL_FOLDER / '_internal'
INTERNAL_DATABASE_FPATH = INTERNAL_FOLDER / 'sofalite.db'
INTERNAL_REPORT_FOLDER = INTERNAL_FOLDER / 'reports'
CUSTOM_STYLES_FOLDER = LOCAL_FOLDER / 'custom_styles'
CUSTOM_DBS_FOLDER = LOCAL_FOLDER / 'custom_databases'

YAML_FPATH = Path('/home/g/projects/sofalite/store/var_labels.yaml')
VAR_LABELS = yaml2varlabels(YAML_FPATH)

class DbeName(StrEnum):  ## database engine
    SQLITE = 'sqlite'

@dataclass(frozen=True)
class DbeSpec:
    """
    entity: e.g. table name 'demo_tbl'
    string value: e.g. 'New Zealand'
    """
    dbe_name: str
    if_clause: str
    placeholder: str
    left_entity_quote: str  ## usually left and right are the same but in MS Access and MS SQL Server they are different: '[' and ']'
    right_entity_quote: str
    gte_not_equals: str
    cartesian_joiner: str
    str_value_quote: str
    str_value_quote_escaped: str
    summable: str

    def entity_quoter(self, entity: str) -> str:
        """
        E.g. "demo_tbl" -> "`demo_tbl`"
        or "table name with spaces" -> "`table name with spaces`"
        for use in
        SELECT * FROM `table name with spaces`
        """
        return f"{self.left_entity_quote}{entity}{self.right_entity_quote}"

    def str_value_quoter(self, str_value: str) -> str:
        """
        E.g. "New Zealand" -> "'New Zealand'"
        for use in
        SELECT * FROM `demo_tbl` WHERE `country` = 'New Zealand'
        """
        return f"{self.str_value_quote}{str_value}{self.str_value_quote}"
