import os
from pathlib import Path
from subprocess import Popen, PIPE

from sofalite.conf.misc import Platform

def get_local_path(my_platform: Platform) -> Path:
    home_path = Path(os.path.expanduser('~'))
    if my_platform == Platform.LINUX:  ## see https://bugs.launchpad.net/sofastatistics/+bug/952077
        try:
            user_path = Path(str(Popen(['xdg-user-dir', 'DOCUMENTS'],
                stdout=PIPE).communicate()[0], encoding='utf-8').strip())  ## get output i.e. [0]. err is 2nd.
        except OSError:
            user_path = home_path
    else:
        user_path = home_path
    local_path = user_path / 'sofastats'
    return local_path
