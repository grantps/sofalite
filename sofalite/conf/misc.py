from dataclasses import dataclass
from enum import Enum
import platform
from typing import Any, Sequence

SOFALITE_WEB_RESOURCES_ROOT = 'http://www.sofastatistics.com/sofalite'

class StrConst(str, Enum):

    def __str__(self):
        return self.value

    @property
    def str(self):
        """
        Sometimes you really need a true str so here is syntactic sugar
        (e.g. some Pandas operations seem to type check rather than duck type).
        """
        return str(self.value)

class Platform(StrConst):
    LINUX = 'linux'
    WINDOWS = 'windows'
    MAC = 'mac'

PLATFORMS = {'Linux': Platform.LINUX, 'Windows': Platform.WINDOWS, 'Darwin': Platform.MAC}
PLATFORM = PLATFORMS.get(platform.system())

class SortOrder(StrConst):
    VALUE = 'by value'
    LABEL = 'by label'
    INCREASING = 'by increasing frequency'
    DECREASING = 'by decreasing frequency'

@dataclass(frozen=True)
class NiceInitialBinDets:
    """
    Details which will be enough to get initial histogram details when accompanied by the actual values.
    """
    n_bins: int
    lower_limit: float
    upper_limit: float

@dataclass(frozen=True)
class BinWidthDets:
    """
    Widths, ranges, for bins.
    """
    bin_width: float
    lower_limit: float
    upper_limit: float

@dataclass(frozen=True)
class HistogramDetails:
    bins_freqs: Sequence[int]
    lower_real_limit: float
    bin_width: float
    n_extra_points: int
