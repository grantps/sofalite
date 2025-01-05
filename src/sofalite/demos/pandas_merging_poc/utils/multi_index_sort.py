from functools import cache, partial
from itertools import count
from typing import Any

import pandas as pd

from sofalite.conf.tables.misc import BLANK, Metric, Sort

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 500)

def tuple2branch_of_vars_key(orig_tuple: tuple, *, debug=False) -> tuple:
    """
    e.g. ('browser', 'Firefox', 'car', 'AUDI', Metric.FREQ)
    =>
    ('browser', 'car', )

    ('age', '20-29', BLANK, BLANK, Metric.FREQ)
    =>
    ('age', )
    """
    items = []
    for idx in count(0, 2):
        try:
            item = orig_tuple[idx]
        except IndexError:
            break
        if item in Metric or item == BLANK:
            break
        items.append(item)
        if debug:
            print(f"{idx=}")
        if idx > 1_000:
            raise Exception(
                "Seriously?! Over 1,000 items in multi-index tuple?! Something has gone badly wrong! Abort!!")
    items = tuple(items)
    if debug:
        print(f"{orig_tuple} => {items}")
    return tuple(items)

def get_metric2order(metric: Metric) -> int:
    return {Metric.FREQ: 1, Metric.ROW_PCT: 2, Metric.COL_PCT: 3}[metric]

def by_freq(variable: str, lbl: str, df: pd.DataFrame, filts: tuple[tuple[str, str]] | None = None, *,
        increasing=True) -> float:
    df_filt = df.copy().loc[df[variable] == lbl]
    for filt_variable, filt_lbl in filts:
        df_filt = df_filt.loc[df_filt[filt_variable] == filt_lbl]
    freq = len(df_filt)
    if increasing:
        sort_val = freq
    else:
        try:
            sort_val = 1 / freq
        except ZeroDivisionError as e:
            sort_val = 1.1  ## so always at end after lbls with freq of at least one (given we are decreasing)
    return sort_val

def get_tuple_for_sorting(orig_tuple: tuple, *, orders_for_col_tree: dict, lbl2val: dict[tuple[str, str], Any], raw_df: pd.DataFrame, debug=False) -> tuple:
    """
    Use this method for they key arg for sorting
    such as sorting(unsorted_multi_index_list, key=SortUtils.get_tuple_for_sorting)

    E.g.
    ('age', '<20', '__blank__', '__blank__', 'freq')
    =>
    (0, 1, 0, 0, 1)

    ('age', '65+', '__blank__', '__blank__', 'row pct')
    =>
    (0, 5, 0, 0, 2)
    """
    max_idx = len(orig_tuple) - 1
    metric_idx = max_idx
    branch_of_variables_key = tuple2branch_of_vars_key(orig_tuple, debug=debug)
    orders_spec = orders_for_col_tree[branch_of_variables_key]  ## e.g. (1, Sort.LBL, 0, Sort.INCREASING)
    list_for_sorting = []
    variable_value_pairs = []
    if debug:
        print(f"{orig_tuple=}; {max_idx=}; {orders_spec=}")
    for idx in count():
        if idx > max_idx:
            break
        ## get order for sorting
        var_idx = (idx % 2 == 0 and idx != metric_idx)
        val_idx = (idx != var_idx and idx != metric_idx)
        if var_idx:
            variable = orig_tuple[idx]
            if variable == BLANK:
                variable_order = 0  ## never more than one so no order
            else:
                variable_order = orders_spec[idx]
            if debug:
                print(f"{variable=}; {variable_order=}")
            list_for_sorting.append(variable_order)
        elif val_idx:
            variable = orig_tuple[idx - 1]
            lbl = orig_tuple[idx]
            if lbl == BLANK:
                value_order = 0  ## never more than one so no order
            else:
                value_order_spec = orders_spec[idx]
                if value_order_spec == Sort.LBL:
                    value_order = lbl
                elif value_order_spec == Sort.VAL:
                    value_order = lbl2val[(variable, lbl)]
                elif value_order_spec in (Sort.INCREASING, Sort.DECREASING):
                    increasing = (value_order_spec == Sort.INCREASING)
                    filts = tuple(variable_value_pairs)
                    value_order = by_freq(variable, lbl, df=raw_df, filts=filts, increasing=increasing)  ## can't use df as arg for cached function
                else:
                    raise ValueError(f"Unexpected value order spec ({value_order_spec})")
                variable_value_pairs.append((variable, lbl))
            list_for_sorting.append(value_order)
        elif metric_idx:
            metric = orig_tuple[idx]
            metric_order = get_metric2order(metric)
            list_for_sorting.append(metric_order)
        else:
            raise ValueError(f"Unexpected item index ({idx=}) when getting tuple for sorting")
    tuple_for_sorting = tuple(list_for_sorting)
    return tuple_for_sorting

def get_sorted_multi_index_list(unsorted_multi_index_list: list[tuple], *,
        orders_for_col_tree: dict, lbl2val: dict[tuple[str, str], Any], raw_df: pd.DataFrame,
        debug=False) -> list[tuple]:
    """
    :param orders_for_col_tree: e.g.
        {
            ('age', ): (0, Sort.VAL),
            ('browser', 'age', ): (1, Sort.LBL, 0, Sort.VAL),
            ('browser', 'car', ): (1, Sort.LBL, 1, Sort.LBL),
        }
    :param lbl2val: e.g.
        {
            ('age', 1): '< 20',
            ('age', 2): '20-29',
            ...
            ('car', 1): 'BMW',
            ('car', 2): 'PORSCHE',
            ...
        }
    :param raw_df: e.g.
                    id  age            browser  car
        0        1    5            Firefox    7
        ...    ...  ...                ...  ...
        1499  1500    4  Internet Explorer    8
    """
    multi_index_sort_fn = partial(get_tuple_for_sorting,
        orders_for_col_tree=orders_for_col_tree, lbl2val=lbl2val, raw_df=raw_df, debug=debug)
    sorted_multi_index_list = sorted(unsorted_multi_index_list, key=multi_index_sort_fn)
    if debug:
        for row in sorted_multi_index_list:
            print(row)
    return sorted_multi_index_list
