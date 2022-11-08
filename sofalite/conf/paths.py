from sofalite.conf.misc import PLATFORM
from sofalite.utils import paths

LOCAL_PATH = paths.get_local_path(PLATFORM)
INTERNAL_FPATH = LOCAL_PATH / '_internal'
DATABASE_FPATH = INTERNAL_FPATH / 'sofalite.db'
