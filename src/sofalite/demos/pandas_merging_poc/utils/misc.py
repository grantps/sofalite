from copy import deepcopy
from functools import partial
from itertools import count
from typing import Literal, Sequence
from webbrowser import open_new_tab

import pandas as pd
from pandas.io.formats.style import Styler
import numpy as np

from sofalite.conf.tables.misc import PCT_MEASURES, Measure
from sofalite.output.styles.misc import get_generic_css, get_placeholder_css, get_style_spec

def get_tbl_df(
        row_idx_tuples: Sequence[Sequence[str]],
        col_idx_tuples: Sequence[Sequence[str]],
        data: Sequence[Sequence[float]],
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
    ## building and validating
    rows_index = pd.MultiIndex.from_tuples(row_idx_tuples)
    bad_cols = []
    for n, col_idx_tuple in enumerate(col_idx_tuples, 1):
        if col_idx_tuple[-1] not in list(Measure):
            bad_cols.append(str(col_idx_tuple))
    if bad_cols:
        msg = '\n'.join(bad_cols)
        raise Exception(f"All column spec tuples must have a Measure as the last item. The following do not:\n{msg}")
    cols_index = pd.MultiIndex.from_tuples(col_idx_tuples)
    n_index_rows = len(rows_index)
    n_data_rows = len(data)
    if n_data_rows != n_index_rows:
        raise Exception(f"Mismatch between row index and data ({n_data_rows=} vs {n_index_rows=})")
    n_index_cols = len(cols_index)
    n_data_cols = len(data[0])
    if n_data_cols != n_index_cols:
        raise Exception(f"Mismatch between col index and data ({n_data_cols=} vs {n_index_cols=})")
    df = pd.DataFrame(data, index=rows_index, columns=cols_index)
    if debug:
        print(f'RAW df:\n\n{df}')
    ## formatting data
    round2dp = partial(round, ndigits=dp)
    df = df.map(round2dp)
    df = df.map(lambda f: f"{f:.{dp}f}")  ## so if 12.0 and 3 dp we want that to be 12.000
    df = df.map(str)
    ## add % symbol where appropriate
    measure_cols = np.array([col_idx_tuple[-1] for col_idx_tuple in col_idx_tuples])
    pct_idx_mask = list(np.where(np.isin(measure_cols, PCT_MEASURES))[0])
    df.iloc[:, pct_idx_mask] = df.iloc[:, pct_idx_mask].applymap(lambda s: s + '%')
    return df

def set_table_styles(pd_styler: Styler) -> Styler:
    """
    Set styles for the table as a whole.
    Can accept a list of CSS dicts https://pandas.pydata.org/docs/user_guide/style.html#Table-Styles

    Note: it might be expected that setting general table-level styles will be overridden by index-level styles,
    which are naturally more specific.

    Counterintuitively, however, because pandas applies index styles by cell-specific ids
    e.g. #T_dc58a_level1_row0,
    the index styles can be overridden by table-level styles created by pandas which are id then element based
    e.g. #T_dc58a th
    which takes priority based on the CSS rules of precedence.

    So setting colour for th by set_table_styles() here will override
    colour set by apply_index() for individual index cells (th's are used for both col and row index cells).

    Therefore, the things we set here mustn't contradict what is in the indiv index CSS settings.
    """
    headers = {
        "selector": "th",
        "props": "font-weight: bold;",
    }
    pd_styler.set_table_styles([headers, ])  ## changes style.Styler for df (which is invoked when style.to_html() is applied
    return pd_styler

def apply_index_styles(df: pd.DataFrame, style_name: str, pd_styler: Styler, *, axis: Literal['rows', 'columns']) -> Styler:
    """
    Index i.e. row and column headings.

    Index styles are applied as per
    https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.apply_index.html

    Styling is applied by axis (rows or columns),
    and level (how far nested).
    Every cell for that axis and level gets a specific, individual CSS style string.
    In my case I give them all the same CSS for that axis-level combination so it is
    [css_str] * len(s).

    The specific style I give a level depends on whether a first-level variable, other variables, a value, or a measure.

    E.g.
    df.index.levshape
    (2, 5, 2, 3) var, val, var, val
    df.columns.levshape
    (2, 10, 2, 5, 3) var, val, var, val, measure <==== always has one level for measure
    """
    style_spec = get_style_spec(style_name)
    tbl_style_spec = style_spec.table
    n_row_index_levels = df.index.nlevels
    n_col_index_levels = df.columns.nlevels

    def get_css_list(s: pd.Series, css_str: str) -> list[str]:
        css_strs = [css_str] * len(s)
        return css_strs

    def variable_name_first_level(s: pd.Series) -> list[str]:
        css_str = (f"background-color: {tbl_style_spec.var_bg_colour_first_level}; "
            f"color: {tbl_style_spec.var_font_colour_first_level}; "
            "font-size: 14px; font-weight: bold;")
        return get_css_list(s, css_str)

    def variable_name_not_first_level(s: pd.Series) -> list[str]:
        css_str = (f"background-color: {tbl_style_spec.var_bg_colour_not_first_level}; "
            f"color: {tbl_style_spec.var_font_colour_not_first_level}; "
            "font-size: 14px; font-weight: bold;")
        return get_css_list(s, css_str)

    def value(s: pd.Series) -> list[str]:
        css_str = "background-color: white; color: black; font-size: 13px;"
        return get_css_list(s, css_str)

    def measure(s: pd.Series) -> list[str]:
        return get_css_list(s, "background-color: white; color: black;")

    for level_idx in count():
        if axis == 'rows':
            last_level = (level_idx == n_row_index_levels - 1)
        elif axis == 'columns':
            last_level = (level_idx == n_col_index_levels - 1)
        else:
            raise ValueError(f"Unexpected {axis=}")
        is_measure_level = (axis == 'columns' and last_level)
        is_variable = (level_idx % 2 == 0 and not is_measure_level)
        if is_variable:
            style_fn = variable_name_first_level if level_idx == 0 else variable_name_not_first_level
        elif is_measure_level:
            style_fn = measure
        else:  ## val level
            style_fn = value
        pd_styler.apply_index(style_fn, axis=axis, level=level_idx)
        if last_level:
            break
    return pd_styler

def get_html_start(style_name: str) -> str:
    kwargs = {
        'generic_css': get_generic_css(),
        'spaceholder_css': get_placeholder_css(style_name),
        'title': 'Demo Table',
    }
    html_start = """\
    <!DOCTYPE html>
    <head>
    <title>%(title)s</title>
    <style type="text/css">
    <!--
    %(spaceholder_css)s
    %(generic_css)s
    -->
    </style>
    </head>
    <body class="tundra">
    """ % kwargs
    return html_start

def display_tbl(tbl_html: str, tbl_name: str, style_name: str):
    html_start = get_html_start(style_name)
    html = f"""\
    {html_start}
    {tbl_html}
    """
    fpath = f"/home/g/Documents/sofalite/reports/{tbl_name}.html"
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(f"file://{fpath}")

def nest_under_blank(item: list | str, *, n_levels: int) -> list:
    """
    e.g. 'Country' and 2 => ['__blank__', ['__blank__', ['Country', ]]]
    """
    nested = item.copy()
    n = 0
    while n < n_levels:
        nested = ['__blank__', nested]
        n += 1
    return nested

def fill_col_tree_to_longest_length(raw_col_tree: list, *, debug=False) -> list:
    """
                               a
                               |
                ------------------------------
                |                            |
                b                            |
                |                            |
    -----------------------                  |
    |                     |                  |
    c                     d                  e

    [a, [b, [c, ], [d, ], ], [e, ]]

    becomes:
                               a
                               |
                ------------------------------
                |                            |
                b                        __blank__ <== fillers always at end before final item (see HTML table examples)
                |                            |
    -----------------------                  |
    |                     |                  |
    c                     d                  e

    [a, [b, [c, ], [d, ], ], [__blank__, [e, ]]]

    e.g. raw_col_tree ==> col_tree
    ['root',
        ['Age Group', ],
        ['Browser', ['Age Group', ]],
        ['Age Group Repeated', ],
    ]
    ==>
    ['root',
        ['__blank__', ['Age Group', ]],
        ['Browser', ['Age Group', ]],
        ['__blank__', ['Age Group Repeated', ]],
    ]
    """
    sub_trees = raw_col_tree[1:]
    max_sub_tree_len = max(len(sub_tree) for sub_tree in sub_trees)
    filled_sub_trees = []
    for sub_tree in sub_trees:
        if len(sub_tree) < max_sub_tree_len:  ## e.g. ['Age Group', ] has len 1 whereas max is 2
            n_levels_to_add = max_sub_tree_len - len(sub_tree)  ## 2 - 1 = 1
            new_sub_tree = sub_tree.deepcopy()
            raw_final_item = new_sub_tree[-1].copy()  ##


    return ['root', *filled_sub_trees]

def columns_multi_index_fixer(df: pd.DataFrame, raw_col_tree: tuple, *, debug=False) -> pd.DataFrame:
    """
    The problem occurs when the columns of the first df don't include all items in final, concatenated df:

                              root
                               |
            ------------------------------------------
            |                                       |
        Age Group                          Age Group Repeated

    +
                              root
                               |
            ------------------------------------------
            |                  |                     |
        Age Group          Browser         Age Group Repeated  <====== correct order

    =
                              root
                               |
            ------------------------------------------
            |                  |                     |
        Age Group     Age Group Repeated          Browser  <====== alphabetical order (the only safe way of doing this given possibility of multiple options)

    The solution is to force the order as expressed in the original design (not from the dfs themselves).

    How do you force order on a multi-index?
    Well, a multi-index is basically a list of items e.g.
    [
        ['Age Group', '<20', ''],
    ]

    Sort it so variables are by design order;
    values are by either numeric order (value), alphabetical order (label), or by measure underneath (if a final level);
    metrics by a standard order e.g. freq, then (if present), col %, then (if present) row %.

    TODO: this is not just about variable order! Value order is harder.

    Sorts are guaranteed to be stable. That means that when multiple records have the same key, their original order is preserved.
    https://docs.python.org/3/howto/sorting.html
    We can also assign sorted slices to slices e.g.
    a[2:4] = sorted(a[2:4])
    Sort sibling variables in the same order amongst siblings they appear with in the col_tree,
    value levels alphabetically,
    and metrics by some other sort rule (currently undefined).
    How? Sort at level 1 by order amongst siblings on level 1. Then for each, filter, and sort alphabetically.
    """
    col_tree = fill_col_tree_to_longest_length(raw_col_tree, debug=debug)
    print(list(df.columns))

    return df















