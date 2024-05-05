from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class CrossTabSpec:
    row_idx_tuples: Sequence[tuple[str]]
    col_idx_tuples: Sequence[tuple[str]]
    data: Sequence[tuple[float]]
    dp: int
