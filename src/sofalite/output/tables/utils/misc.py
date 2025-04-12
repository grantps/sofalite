from collections.abc import Collection
from functools import partial
from itertools import combinations, count
from typing import Literal, Sequence
from webbrowser import open_new_tab

import pandas as pd
from pandas.io.formats.style import Styler
import numpy as np

from sofalite.conf.style import StyleSpec
from sofalite.conf.tables.misc import TOTAL
from sofalite.conf.tables.output.cross_tab import TblSpec as CrossTabTblSpec
from sofalite.conf.tables.output.freq import TblSpec as FreqTabTblSpec
from sofalite.conf.tables.misc import PCT_METRICS, Metric
from sofalite.output.styles.misc import get_generic_css, get_placeholder_css

def correct_str_dps(val: str, *, dp: int) -> str:
    """
    Apply decimal points to floats only - leave Freq integers alone.
    3dp
    0.0 => 0.000
    12 => 12
    """
    try:
        len_after_dot = len(val.split('.')[1])
    except IndexError:
        return val
    n_zeros2add = dp - len_after_dot
    zeros2add = '0' * n_zeros2add
    return val + zeros2add

def get_raw_df(cur, tbl_spec: CrossTabTblSpec | FreqTabTblSpec, *, debug=False) -> pd.DataFrame:
    cur.execute(f"SELECT * FROM {tbl_spec.src_tbl}")
    data = cur.fetchall()
    df = pd.DataFrame(data, columns=[desc[0] for desc in cur.description])
    if debug:
        print(df)
    return df

def get_data_from_spec(cur, tbl_spec: CrossTabTblSpec | FreqTabTblSpec,
        all_variables: Collection[str], totalled_variables: Collection[str], *, debug=False) -> list[list]:
    """
    rows: country (TOTAL) > gender (TOTAL)
    cols: agegroup (TOTAL, Freq)
    filter: WHERE agegroup <> 4
        AND browser NOT IN ('Internet Explorer', 'Opera', 'Safari')

    Needed:
    data_main + data_total_agegroup
        + data_total_gender + data_total_gender_agegroup
        + data_total_country + data_total_country_agegroup
        + data_total_country_gender + data_total_country_gender_agegroup

    main = the row + col fields (filtered) and count
    totals for each var with a TOTAL = "{TOTAL}" AS totalled var, other vars, filter, group by non-totalled
    two-way combos

    For more complex situation - e.g. country_gender_by_browser_and_age_group
    data = (
        All - every variable, group by every variable
        data_main
        Then, for all the totalled variables:
        1s - each var gets TOTAL version
        + data_total_agegroup + data_total_browser + data_total_gender + data_total_country
        2s - a,b a,c a,d   b,c b,d   c,d (every 2-way combination)
        + data_total_browser_agegroup + data_total_country_browser + data_total_gender_browser
        + data_total_gender_agegroup + data_total_country_gender
        + data_total_country_agegroup
        3s - a,b,c a,b,d a,c,d   b,c,d  (every 3-way combination)
        + data_total_gender_browser_agegroup + data_total_country_gender_browser
        + data_total_country_browser_agegroup + data_total_country_gender_agegroup
        4s - a,b,c,d (every 4-way combination)
        + data_total_country_gender_browser_agegroup
        if we had N variables we want all combos with N, all combos with N-1, ... all combos with 1
    )

    Note - order matters

    Step 0 - get all variables that are to be totalled
        (if any - and note, their order, place in the variable hierarchy, or row vs col, is irrelevant)
        and all non-totalled variables (if any)
    Step 1 - select and group by all variables
    Step 2 - for any totalled variables, get every combination from 1 to N
        (where N is the total number of totalled variables) and then generate the SQL and data (lists of col-val lists)
    Step 3 - concat all data (data + ...)
    """
    data = []
    ## Step 0 - variable lists
    n_totalled = len(totalled_variables)
    ## Step 1 - group by all
    main_flds = ', '.join(all_variables)
    sql_main = f"""\
    SELECT {main_flds}, COUNT(*) AS n
    FROM {tbl_spec.src_tbl}
    {tbl_spec.tbl_filter}
    GROUP BY {main_flds}
    """
    cur.execute(sql_main)
    data.extend(cur.fetchall())
    ## Step 2 - combos
    totalled_combinations = []
    if n_totalled:
        for n in count(1):
            totalled_combinations_for_n = combinations(totalled_variables, n)
            totalled_combinations.extend(totalled_combinations_for_n)
            if n == n_totalled:  ## might be 0
                break
    if debug: print(f"{totalled_combinations=}")
    for totalled_combination in totalled_combinations:  ## there might not be any, of course
        if debug: print(totalled_combination)
        ## have to preserve order of variables - follow order of all_variables
        select_clauses = []
        group_by_vars = []
        for var in all_variables:
            if var in totalled_combination:
                select_clauses.append(f'"{TOTAL}" AS {var}')
            else:
                select_clauses.append(var)
                group_by_vars.append(var)
        select_str = "SELECT " + ', '.join(select_clauses) + ", COUNT(*) AS n"
        group_by = "GROUP BY " + ', '.join(group_by_vars) if group_by_vars else ''
        sql_totalled = f"""\
        {select_str}
        FROM {tbl_spec.src_tbl}
        {tbl_spec.tbl_filter}
        {group_by}
        """
        if debug: print(f"sql_totalled={sql_totalled}")
        cur.execute(sql_totalled)
        data.extend(cur.fetchall())
    if debug:
        for row in data:
            print(row)
    return data

def get_order_rules_for_multi_index_branches(tbl_spec: CrossTabTblSpec | FreqTabTblSpec) -> dict:
    """
    Should come from a GUI via an interface ad thence into the code using this.

    Note - to test Sort.INCREASING and Sort.DECREASING I'll need to manually check what expected results should be (groan)

    Note - because, below the top-level, only chains are allowed (not trees)
    the index for any variables after the first (top-level) are always 0.
    """
    orders = {}
    dims_type_specs = [tbl_spec.row_specs, ]
    try:
        dims_type_specs.append(tbl_spec.col_specs)
    except AttributeError:
        pass
    for dim_type_specs in dims_type_specs:
        for top_level_idx, dim_type_spec in enumerate(dim_type_specs):
            dim_vars = tuple(dim_type_spec.self_and_descendant_vars)
            sort_dets = []
            for chain_idx, dim_spec in enumerate(dim_type_spec.self_and_descendants):
                idx2use = top_level_idx if chain_idx == 0 else 0
                sort_dets.extend([idx2use, dim_spec.sort_order])
            orders[dim_vars] = tuple(sort_dets)
    return orders

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
        if col_idx_tuple[-1] not in list(Metric):
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
    pct_idx_mask = list(np.where(np.isin(measure_cols, PCT_METRICS))[0])
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

    Therefore, the things we set here mustn't contradict what is in the indiv index CSS settings
    in apply_index_styles() below.
    """
    headers = {
        "selector": "th",
        "props": "font-weight: bold;",
    }
    pd_styler.set_table_styles([headers, ])  ## changes style.Styler for df (which is invoked when style.to_html() is applied
    return pd_styler

def apply_index_styles(
        df: pd.DataFrame, style_spec: StyleSpec, pd_styler: Styler, *, axis: Literal['rows', 'columns']) -> Styler:
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
    tbl_style_spec = style_spec.table
    n_row_index_levels = df.index.nlevels
    n_col_index_levels = df.columns.nlevels

    def get_css_list(s: pd.Series, css_str: str) -> list[str]:
        css_strs = [css_str] * len(s)
        return css_strs

    def variable_name_first_level(s: pd.Series) -> list[str]:
        css_str = (f"background-color: {tbl_style_spec.var_bg_colour_first_level}; "
            f"color: {tbl_style_spec.var_font_colour_first_level}; "
            "font-size: 14px; font-weight: bold; "
            f"border: solid 1px {tbl_style_spec.var_border_colour_first_level};")
        return get_css_list(s, css_str)

    def variable_name_not_first_level(s: pd.Series) -> list[str]:
        css_str = (f"background-color: {tbl_style_spec.var_bg_colour_not_first_level}; "
            f"color: {tbl_style_spec.var_font_colour_not_first_level}; "
            "font-size: 14px; font-weight: bold;"
            f"border: solid 1px {tbl_style_spec.var_border_colour_not_first_level};")
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
