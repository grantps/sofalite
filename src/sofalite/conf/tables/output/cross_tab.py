from collections.abc import Collection
from dataclasses import dataclass
from itertools import product

from sofalite.conf.misc import VarLabels
from sofalite.conf.tables.output.common import DimSpec

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
