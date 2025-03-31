from enum import StrEnum
from pathlib import Path
import platform

SOFALITE_WEB_RESOURCES_ROOT = 'http://www.sofastatistics.com/sofalite'
SOFALITE_FS_RESOURCES_ROOT = Path('/home/g/Documents/sofastats/reports/sofastats_report_extras')

class Platform(StrEnum):
    LINUX = 'linux'
    WINDOWS = 'windows'
    MAC = 'mac'

PLATFORMS = {'Linux': Platform.LINUX, 'Windows': Platform.WINDOWS, 'Darwin': Platform.MAC}
PLATFORM = PLATFORMS.get(platform.system())
