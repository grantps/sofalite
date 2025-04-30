## depends on stats_calc and utils which are lower level - so no problematic project dependencies :-)
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from statistics import median

from sofalite.stats_calc.boxplot import get_bottom_whisker, get_top_whisker
from sofalite.stats_calc.histogram import BinDets  ## noqa - so available for import from here as the one-stop shop for stats interfaces
from sofalite.utils.stats import get_quartiles

## samples

@dataclass(frozen=True)
class Sample:
    """
    Sample including label.
    To refer to the vals of a sample call them "sample_vals" not "sample" to prevent confusion.
    "sample" must always mean an object with both lbl and vals.
    If there are multiple sample_vals call it "samples_vals" not "samples".
    "samples" should only ever refer to a sequence of Sample objects.
    Sample dets refers primarily to metadata about sample values e.g. min, max, mean.
    A "vals" attribute is included.
    """
    lbl: str
    vals: Sequence[float]

@dataclass(frozen=True, kw_only=True)
class NumericSampleDets:
    lbl: str
    n: int
    mean: float
    stdev: float
    sample_min: float
    sample_max: float
    ci95: tuple[float, float] | None = None

@dataclass(frozen=True, kw_only=True)
class NumericSampleDetsExt(NumericSampleDets):
    kurtosis: float | str
    skew: float | str
    p: float | str
    vals: Sequence[float]

@dataclass(frozen=True)
class NumericSampleDetsFormatted:
    """
    Just the fields needed for tabular display as output.
    Usually formatted with decimal places and p in a helpful string already
    """
    lbl: str
    n: str
    mean: str
    ci95: str
    stdev: str
    sample_min: str
    sample_max: str
    kurtosis: str
    skew: str
    p: str

## other

@dataclass(frozen=True)
class OrdinalResult:
    lbl: str
    n: int
    median: float
    sample_min: float
    sample_max: float

@dataclass(frozen=True)
class Result(OrdinalResult):
    mean: float | None = None
    stdev: float | None = None

@dataclass(frozen=True)
class MannWhitneyDets:
    lbl: str
    n: int
    avg_rank: float
    median: float
    sample_min: float
    sample_max: float

@dataclass(frozen=True)
class MannWhitneyDetsExt:
    lbl_1: str
    lbl_2: str
    n_1: int
    n_2: int
    ranks_1: list[int]
    val_dets: list[dict]
    sum_rank_1: int
    u_1: float
    u_2: float
    u: float

@dataclass(frozen=True)
class WilcoxonDetsExt:
    diff_dets: list[dict]
    ranking_dets: list[dict]
    plus_ranks: list[int]
    minus_ranks: list[int]
    sum_plus_ranks: float
    sum_minus_ranks: float
    t: float
    n: int

@dataclass(frozen=True)
class SpearmansDets:
    initial_tbl: list
    x_and_rank: list[tuple]
    y_and_rank: list[tuple]
    n_x: int
    n_cubed_minus_n: int
    tot_d_squared: float
    tot_d_squared_x_6: float
    pre_rho: float
    rho: float

@dataclass(frozen=True)
class SpearmansInitTbl:
    x: float
    y: float
    rank_x: int
    rank_y: int
    diff: int
    diff_squared: int

## https://medium.com/@aniscampos/python-dataclass-inheritance-finally-686eaf60fbb5
@dataclass(frozen=True, kw_only=True)
class AnovaResult:
    p: float | Decimal
    F: float | Decimal
    groups_dets: Sequence[NumericSampleDetsExt]
    sum_squares_within_groups: float | Decimal
    degrees_freedom_within_groups: float
    mean_squares_within_groups: float | Decimal
    sum_squares_between_groups: float | Decimal
    degrees_freedom_between_groups: int
    mean_squares_between_groups: float | Decimal
    obriens_msg: str

@dataclass(frozen=True, kw_only=True)
class AnovaResultExt(AnovaResult):
    group_lbl: str
    measure_fld_lbl: str

@dataclass(frozen=True, kw_only=True)
class TTestResult:
    """
    p is the two-tailed probability
    """
    t: float | Decimal
    p: float | Decimal
    group_a_dets: NumericSampleDetsExt
    group_b_dets: NumericSampleDetsExt
    degrees_of_freedom: float
    obriens_msg: str

@dataclass(frozen=True, kw_only=True)
class TTestIndepResultExt(TTestResult):
    group_lbl: str
    measure_fld_lbl: str

@dataclass(frozen=True)
class NormalTestResult:
    k2: float | None
    p: float | None
    c_skew: float | None
    z_skew: float | None
    c_kurtosis: float | None
    z_kurtosis: float | None

@dataclass(frozen=True)
class RegressionDets:
    slope: float
    intercept: float
    r: float
    x0: float
    y0: float
    x1: float
    y1: float

class SortOrder(StrEnum):
    VALUE = 'by value'
    LABEL = 'by label'
    INCREASING = 'by increasing frequency'
    DECREASING = 'by decreasing frequency'

class BoxplotType(StrEnum):
    MIN_MAX_WHISKERS = 'min_max_whiskers'
    HIDE_OUTLIERS = 'hide_outliers'
    IQR_1_PT_5_OR_INSIDE = '1.5 IQR or inside'

@dataclass(frozen=False)
class BoxDets:
    vals: Sequence[float]
    boxplot_type: BoxplotType = BoxplotType.IQR_1_PT_5_OR_INSIDE

    def __post_init__(self):
        """
        lower_box_val=box_dets.lower_box_val,
        upper_box_val=box_dets.upper_box_val,
        """
        min_measure = min(self.vals)
        max_measure = max(self.vals)
        ## box
        lower_quartile, upper_quartile = get_quartiles(self.vals)
        self.box_bottom = lower_quartile
        self.box_top = upper_quartile
        ## median
        self.median = median(self.vals)
        ## whiskers
        if self.boxplot_type == BoxplotType.MIN_MAX_WHISKERS:
            self.bottom_whisker = min_measure
            self.top_whisker = max_measure
        else:
            iqr = self.box_top - self.box_bottom
            raw_bottom_whisker = self.box_bottom - (1.5 * iqr)
            raw_top_whisker = self.box_top + (1.5 * iqr)
            self.bottom_whisker = get_bottom_whisker(raw_bottom_whisker, self.box_bottom, self.vals)
            self.top_whisker = get_top_whisker(raw_top_whisker, self.box_top, self.vals)
        ## outliers
        if self.boxplot_type == BoxplotType.IQR_1_PT_5_OR_INSIDE:
            self.outliers = [x for x in self.vals
                if x < self.bottom_whisker or x > self.top_whisker]
        else:
            self.outliers = []  ## hidden or inside whiskers
