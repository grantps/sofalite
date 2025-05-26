from collections.abc import Sequence
from dataclasses import dataclass

@dataclass(frozen=True)
class ChiSquareData:
    """
    Everything we can derive from the source data before we actually do the statistical analysis.
    """
    variable_a_values: Sequence[float | str]  ## e.g. Korea, NZ, USA found in variable A (that also had values in variable B)
    variable_b_values: Sequence[float | str]  ## e.g. Badminton, Basketball, Football, Tennis found in variable B (that also had values in variable A)
    observed_values_ordered: list[float]
    expected_values_same_order: list[float]  ## maintains same order so they can be compared by cell
    minimum_cell_count: int
    pct_cells_freq_under_5: float
    degrees_of_freedom: int
