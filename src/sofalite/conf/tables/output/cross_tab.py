from collections.abc import Collection
from dataclasses import dataclass
from enum import StrEnum
from itertools import product
from typing import Self

from sofalite.conf.misc import VarLabels
from sofalite.conf.tables.misc import Metric, Sort

class PctType(StrEnum):
    ROW_PCT = 'Row %'
    COL_PCT = 'Col %'

@dataclass(frozen=False)
class DimSpec:
    var: str
    has_total: bool = False
    is_col: bool = False
    pct_metrics: Collection[Metric] | None = None
    sort_order: Sort = Sort.VAL
    child: Self | None = None

    @property
    def descendant_vars(self) -> list[str]:
        """
        All variables under, but not including, this Dim.
        Note - only includes chains, not trees, as a deliberate design choice to avoid excessively complicated tables.
        Tables are for computers to make, but for humans to read and understand :-).
        """
        dim_vars = []
        if self.child:
            dim_vars.append(self.child.var)
            dim_vars.extend(self.child.descendant_vars)
        return dim_vars

    @property
    def self_and_descendants(self) -> list[Self]:
        """
        All Dims under, and including, this Dim.
        """
        dims = [self, ]
        if self.child:
            dims.extend(self.child.self_and_descendants)
        return dims

    @property
    def self_and_descendant_vars(self) -> list[str]:
        return [dim.var for dim in self.self_and_descendants]

    @property
    def self_and_descendant_totalled_vars(self) -> list[str]:
        """
        All variables under, and including, this Dim that are totalled (if any).
        """
        return [dim.var for dim in self.self_and_descendants if dim.has_total]

    @property
    def self_or_descendant_pct_metrics(self) -> Collection[Metric] | None:
        if self.pct_metrics:
            return self.pct_metrics
        elif self.child:
            return self.child.self_or_descendant_pct_metrics
        else:
            return None

    def __post_init__(self):
        if self.pct_metrics:
            if self.child:
                raise ValueError(f"Metrics are only for terminal dimension specs e.g. a > b > c (can have metrics)")
            if not self.is_col:
                raise ValueError(f"Metrics are only for terminal column specs, yet this is a row spec")
        if self.child:
            if not self.is_col == self.child.is_col:
                raise ValueError(f"This dim has a child that is inconsistent e.g. a col parent having a row child")
        if self.var in self.descendant_vars:
            raise ValueError(
                f"Variables can't be repeated in the same dimension spec e.g. Car > Country > Car. Variable {self.var}")


@dataclass(frozen=True, kw_only=True)
class TblSpec:
    src_tbl: str
    tbl_filter: str | None
    row_specs: list[DimSpec]
    col_specs: list[DimSpec]
    var_labels: VarLabels

    @staticmethod
    def _get_dupes(_vars: Collection[str]) -> set[str]:
        dupes = set()
        seen = set()
        for var in _vars:
            if var in seen:
                dupes.add(var)
            else:
                seen.add(var)
        return dupes

    @property
    def totalled_vars(self) -> list[str]:
        tot_vars = []
        for row_spec in self.row_specs:
            tot_vars.extend(row_spec.self_and_descendant_totalled_vars)
        for col_spec in self.col_specs:
            tot_vars.extend(col_spec.self_and_descendant_totalled_vars)
        return tot_vars

    def _get_max_dim_depth(self, *, is_col=False) -> int:
        max_depth = 0
        dim_specs = self.col_specs if is_col else self.row_specs
        for dim_spec in dim_specs:
            dim_depth = len(dim_spec.self_and_descendant_vars)
            if dim_depth > max_depth:
                max_depth = dim_depth
        return max_depth

    @property
    def max_row_depth(self) -> int:
        return self._get_max_dim_depth()

    @property
    def max_col_depth(self) -> int:
        return self._get_max_dim_depth(is_col=True)

    def __post_init__(self):
        row_dupes = TblSpec._get_dupes([spec.var for spec in self.row_specs])
        if row_dupes:
            raise ValueError(f"Duplicate top-level variable(s) detected in row dimension - {sorted(row_dupes)}")
        col_dupes = TblSpec._get_dupes([spec.var for spec in self.col_specs])
        if col_dupes:
            raise ValueError(f"Duplicate top-level variable(s) detected in column dimension - {sorted(col_dupes)}")
        ## var can't be in both row and col e.g. car vs country > car
        for row_spec, col_spec in product(self.row_specs, self.col_specs):
            row_spec_vars = set([row_spec.var] + row_spec.descendant_vars)
            col_spec_vars = set([col_spec.var] + col_spec.descendant_vars)
            overlapping_vars = row_spec_vars.intersection(col_spec_vars)
            if overlapping_vars:
                raise ValueError("Variables can't appear in both rows and columns. "
                    f"Found the following overlapping variable(s): {', '.join(overlapping_vars)}")
