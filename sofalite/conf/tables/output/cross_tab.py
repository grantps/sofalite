from typing import Sequence

import pandas as pd

def get_tbl_df(
        row_idx_tuples: Sequence[tuple[str]],
        col_idx_tuples: Sequence[tuple[str]],
        data: Sequence[tuple[float]],
        *, dp: int, debug=False) -> pd.DataFrame:
    """
    Work with floats as inputs but everything coming out will be strings ready to display.
    So rounding to dp will be applied and %s will be added to percentages.
    Validation will occur to align row and column indexes with data.

    :param row_idx_tuples:
    :param col_idx_tuples:
    :param dp: decimal points
    :return:
    """
    rows_index = pd.MultiIndex.from_tuples(row_idx_tuples)
    cols_index = pd.MultiIndex.from_tuples(col_idx_tuples)
    ## validate
    n_index_rows = len(rows_index)
    n_data_rows = len(data)
    if n_data_rows != n_index_rows:
        raise Exception(f"Mismatch between row index and data ({n_data_rows=} vs {n_index_rows=})")
    n_index_cols = len(cols_index)
    n_data_cols = len(data[0])
    if n_data_cols != n_index_cols:
        raise Exception(f"Mismatch between col index and data ({n_data_cols=} vs {n_index_cols=})")
    ## final
    df = pd.DataFrame(data, index=rows_index, columns=cols_index)
    if debug:
        print(df)
    return df
