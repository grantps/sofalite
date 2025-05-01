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

MAX_RANK_DATA_VALS = 100_000

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
DATABASE_FOLDER = INTERNAL_FOLDER / 'sofalite.db'
INTERNAL_REPORT_FOLDER = INTERNAL_FOLDER / 'reports'
CUSTOM_STYLES_FOLDER = LOCAL_FOLDER / 'custom_styles'

YAML_FPATH = Path('/home/g/projects/sofalite/store/var_labels.yaml')
VAR_LABELS = yaml2varlabels(YAML_FPATH)
