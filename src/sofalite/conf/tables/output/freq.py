from dataclasses import dataclass

from sofalite.conf.misc import VarLabels
from sofalite.conf.tables.output.common import DimSpec

@dataclass(frozen=True, kw_only=True)
class TblSpec:
    src_tbl: str
    tbl_filter: str | None
    row_specs: list[DimSpec]
    var_labels: VarLabels
    inc_col_pct: bool = False

    @property
    def totalled_vars(self) -> list[str]:
        tot_vars = []
        for row_spec in self.row_specs:
            tot_vars.extend(row_spec.self_and_descendant_totalled_vars)
        return tot_vars

    @property
    def max_row_depth(self) -> int:
        max_depth = 0
        for row_spec in self.row_specs:
            row_depth = len(row_spec.self_and_descendant_vars)
            if row_depth > max_depth:
                max_depth = row_depth
        return max_depth

    def __post_init__(self):
        row_vars = [spec.var for spec in self.row_specs]
        row_dupes = set()
        seen = set()
        for row_var in row_vars:
            if row_var in seen:
                row_dupes.add(row_var)
            else:
                seen.add(row_var)
        if row_dupes:
            raise ValueError(f"Duplicate top-level variable(s) detected in row dimension - {sorted(row_dupes)}")
