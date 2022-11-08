from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional, Sequence

MAX_RANKDATA_VALS = 100_000

@dataclass(frozen=True)
class Sample:
    lbl: str
    sample: Sequence[Any]

@dataclass(frozen=True, kw_only=True)
class NumericSampleDets:
    lbl: str
    n: int
    mean: float
    stdev: float
    sample_min: float
    sample_max: float
    ci95: Optional[tuple[float, float]] = None

@dataclass(frozen=True, kw_only=True)
class NumericSampleDetsExt(NumericSampleDets):
    kurtosis: float | str
    skew: float | str
    p: float | str

@dataclass(frozen=True)
class OrdinalResult:
    lbl: str
    n: int
    median: float
    sample_min: float
    sample_max: float

@dataclass(frozen=True)
class Result(OrdinalResult):
    mean: Optional[float] = None
    stdev: Optional[float] = None

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

@dataclass(frozen=True)
class NormalTestResult:
    k2: float | None
    p: float | None
    cskew: float | None
    zskew: float | None
    ckurtosis: float | None
    zkurtosis: float | None
