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

@dataclass(frozen=False)
class BinDets:
    lower_limit: float
    upper_limit: float
    n_bins: int
    bin_width: float

    def validate(self):
        expected_n_bins = round(self.range / self.bin_width)
        if self.n_bins != expected_n_bins:
            raise ValueError(f"{self.n_bins} not expected value {expected_n_bins} "
                f"as calculated from {self.lower_limit=}, {self.upper_limit=}, and {self.bin_width=}")

    def __post_init__(self):
        self.range = self.upper_limit - self.lower_limit
        self.validate()
        bin_start = self.lower_limit
        self.bin_ranges = []
        for bin_n in range(1, self.n_bins + 1):
            bin_end = bin_start + self.bin_width
            self.bin_ranges.append((bin_start, bin_end))
            bin_start = bin_end

    def to_bin_lbls(self, *, dp: int = 3):
        rounded_bin_ranges = []
        for raw_bin_start, raw_bin_end in self.bin_ranges:
            ## if ints
            rounded_start = round(raw_bin_start, dp)
            if rounded_start == int(rounded_start):
                bin_start = int(rounded_start)
            else:
                bin_start = rounded_start
            rounded_end = round(raw_bin_end, dp)
            if rounded_end == int(rounded_end):
                bin_end = int(rounded_end)
            else:
                bin_end = rounded_end
            rounded_bin_ranges.append((bin_start, bin_end))
        bin_lbls = [f"{lower} to < {upper}" for lower, upper in rounded_bin_ranges]
        bin_lbls[-1] = bin_lbls[-1].replace('<', '<=')
        return bin_lbls
