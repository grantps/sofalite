"""
Central idea - multi-indexes need sorting. Multi-indexes are basically lists so sorting is simple at one level.
We should be able to use sorting or .sort() with a clever sort function as the key argument.
Basically we convert a row into a tuple that, when sorted upon as the key, orders the multi-index rows as configured.

E.g. imagine we start with an index like this:
[
  ['a', 'cat', 'banana', 123],
  ['b', 'dog', 'apple', 989],
]

We then apply a function to the list to create a sorting-ready tuple. E.g.:

['a', 'cat', 'banana', 123]
=>
(1, 12, 2, 5)  ## Note - not necessarily alphabetical - might be based on the values underlying the labels or something
and
['b', 'dog', 'apple', 989]
=> (0, 3, 6, 12)  ## also, just for the purposes of illustration, imagine if this were the result of the same function

Simple sorting would put (0, 3, 6, 12) before (1, 12, 2, 5) and so we would end up with the following sorted multi-index:
[
  ['b', 'dog', 'apple', 989],
  ['a', 'cat', 'banana', 123],
]

So how should sorting occur?

There are two things being sorted. Variables and values e.g. agegroup and '< 20', '20-29' etc.
Variables get their sort order from the order in which they are configured in the table design.
For example, if we have the following variable design:

      agegroup                    browser
         |                           |
         |              ----------------------------
         |              |                          |
         |          agegroup                      car

we end up with a df like:

     Age Group                                       Web Browser
Young  Middle  Old                       Firefox                                      Chrome
                           Age Group               Car                   Age Group               Car
                      Young  Middle  Old    Tesla  Mini  Porsche    Young  Middle  Old    Tesla  Mini  Porsche
Freq   Freq    Freq   Freq   Freq   Freq    Freq   Freq  Freq       Freq   Freq   Freq    Freq   Freq  Freq
--------------------------------------------------------------------------------------------------------------

and a multi-index like:
[
  ...
  ('Age Group', 'Middle', '__blank__', '__blank__', 'Freq'),
  ...
  ('Web Browser', 'Chrome', 'Age Group', 'Young', 'Freq'),
  ...
]

We need to first configure the sort order:

Remember, there are two parts - variables, and their values. The variables are simple index values based on the order
they were configured. E.g. at the top level, agegroup is 0 and browser 1.
Under browser, agegroup is 0, and car is 1.
For values, we have three sort order options - by value e.g. 1 then 2 then 3 etc.;
by label e.g. 'Apple', then 'Banana' etc.; or by frequency (subdivided into either increasing or decreasing).
We also have the measure / metric where Freq then Row % then Col %.

So ... we might have:

               age   age  (no need to define sort order for measures - standard and fixed)
               var   val
                |     |
{               v     v
    ('age', ): (0, Sort.VAL),
                               browser  browser   age   age
                                 var      val     var   val
                                  |        |       |    |
                                  v        v       v    v
    ('browser', 'age', ):        (1,    Sort.LBL,  0, Sort.VAL),

                               browser  browser   car   car
                                 var      val     var   val
                                  |        |       |    |
                                  v        v       v    v
    ('browser', 'car', ):        (1, Sort.LBL, 1, Sort.LBL),
}

Then apply the sort order knowing it is var, val, ... (skipping __blank__ - leave it as is), measure:

('Age Group', 'Middle', '__blank__', '__blank__', 'Freq'),

TODO: assumption - Variable labels must always be different for different variables. No duplicates.

"""
from functools import partial
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
    Use this method for the key arg for sorting
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
    :param lbl2val: so we can get from label to value when all we have is the label. Used when we need to sort by value
     even though the cell content is the label. E.g.
        {
            ('age', '< 20'): 1,
            ('age', '20-29'): 2,
            ...
            ('car', 'BMW'): 1,
            ('car', 'PORSCHE'): 2,
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
