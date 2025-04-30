from collections.abc import Collection
from functools import partial
from itertools import combinations, count
from typing import Literal, Sequence
from webbrowser import open_new_tab

import pandas as pd
from pandas.io.formats.style import Styler
import numpy as np

from sofalite.output.styles.interfaces import StyleSpec
from sofalite.output.styles.utils import get_generic_unstyled_css, get_styled_placeholder_css_for_main_tbls
from sofalite.output.tables.interfaces import DimSpec
from sofalite.output.tables.interfaces import PCT_METRICS, TOTAL, Metric, PctType

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

def get_raw_df(cur, src_tbl: str, *, debug=False) -> pd.DataFrame:
    cur.execute(f"SELECT * FROM {src_tbl}")
    data = cur.fetchall()
    df = pd.DataFrame(data, columns=[desc[0] for desc in cur.description])
    if debug:
        print(df)
    return df

def get_data_from_spec(cur, src_tbl: str, tbl_filt_clause: str,
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
    FROM {src_tbl}
    {tbl_filt_clause}
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
        FROM {src_tbl}
        {tbl_filt_clause}
        {group_by}
        """
        if debug: print(f"sql_totalled={sql_totalled}")
        cur.execute(sql_totalled)
        data.extend(cur.fetchall())
    if debug:
        for row in data:
            print(row)
    return data

def _round_kws(x, *, dp: int) -> float:
    """
    Need kwargs so we can use with partial given we are not changing the first positional args - see
    https://stackoverflow.com/questions/11173660/can-one-partially-apply-the-second-argument-of-a-function-that-takes-no-keyword
    """
    return round(x, dp)

def get_df_pre_pivot_with_pcts(df: pd.DataFrame, *,
        is_cross_tab=True, pct_type: PctType, dp: int = 2, debug=False) -> pd.DataFrame:
    """
    Strategy - we have multi-indexes so let's use them!
    Note - exact same approach works if you work from the df (for rows and Row %) or from a transposed df (for cols and Col %)

    browser_var                                                 Web Browser
    browser                                                          Chrome                          Firefox                           Chrome   Firefox     TOTAL
    agegroup_var                                                  Age Group                        Age Group                        Age Group Age Group Age Group
    agegroup                                                           < 20 20-29 30-39 40-64  65+      < 20 20-29 30-39 40-64  65+     TOTAL     TOTAL      < 20 20-29 30-39 40-64  65+ TOTAL
    metric                                                             Freq  Freq  Freq  Freq Freq      Freq  Freq  Freq  Freq Freq      Freq      Freq      Freq  Freq  Freq  Freq Freq  Freq
    home_country_var home_country row_filler_var_0 row_filler_0
    Home Country     NZ           __blank__        __blank__             18     8    10    27   30        35    25    24    51   55        93       190        53    33    34    78   85   283
                     South Korea  __blank__        __blank__             32    17    16    35   21        49    23    17    43   49       121       181        81    40    33    78   70   302
                     TOTAL        __blank__        __blank__             60    44    43    90   95       109    74    55   132  152       332       522       169   118    98   222  247   854
                     USA          __blank__        __blank__             10    19    17    28   44        25    26    14    38   48       118       151        35    45    31    66   92   269

    Row %s are taken row (per column block e.g. Under Chrome, or under Firefox) per row.
    We have all the numbers we need so surely there must be some way to calculate it (spoiler - there is!).
    We can do it row by row if we have the information required available in the row. So do we? Let's look at a row:

    Each row is a Series with a multi-index on the left and the values on the right. E.g.:

    browser_var  browser  agegroup_var  agegroup  metric
    Web Browser  Chrome   Age Group     < 20      Freq        18
                                        20-29     Freq         8
                                        30-39     Freq        10
                                        40-64     Freq        27
                                        65+       Freq        30
                 Firefox  Age Group     < 20      Freq        35
                                        20-29     Freq        25
                                        30-39     Freq        24
                                        40-64     Freq        51
                                        65+       Freq        55
                 Chrome   Age Group     TOTAL     Freq        93
                 Firefox  Age Group     TOTAL     Freq       190
                 TOTAL    Age Group     < 20      Freq        53
                                        20-29     Freq        33
                                        30-39     Freq        34
                                        40-64     Freq        78
                                        65+       Freq        85
                                        TOTAL     Freq       283

    Looking at it like this, we can see a way of using aggregation and broadcasting to get row %s.
    In the case above, if we can group by Web Browser,
    and broadcast the total within each group as the denominator of every value in the group,
    (multiply by 100, of course, so a percentage not a fraction).
    One more complication: if TOTAL is included, need to divide the percentage by 2
    because the inclusion of TOTAL doubles it.
    One more complication: have to do the aggregation slightly differently if no variable to group by.

    OK - let's do a worked example using the row Series.
    In Chrome we have a total of 18+8+10+27+30+93 (you nearly forgot the TOTAL row didn't you!).
    So that's 93x2 i.e. 186.
    (100 * 18) / (186 / 2) = 19.35% Correct! :-)
    (100 * 93) / (186 / 2) = 100% of course! Brilliant!

    The rest of the logic is about working out whether or not we have variables to group by;
    getting variable to group by (if any);
    and seeing if there is a TOTAL (so we can tell if we have to divide by 2);

    Finally, we have to gather the results into the same structure as the pre-pivot source data
    BUT with Row % or Col % as the metric not Freq.
    Note - OK if we don't include columns not used in pivot, and OK if the cols are not in the correct order.
    The appending is by col_name so it Just Works™ :-).
    Why? Because if we can get to that structure, we can just append the different dfs-by-metric together,
    and pivot the resulting combined df to get a column per metric.
    Trivial if we can get to that point - it Just Works™!
    """
    if pct_type == PctType.COL_PCT:
        df = df.T  ## if unpivoted, each row has values for the Row % calculation; otherwise has values for Col % calculation. If pivoted, it is the reverse. But still rows refers to rows and cols to cols in the df we're working through here either way.
    row_0 = df.iloc[0]
    var_names = row_0.index.names
    col_names = [col for col in df.columns.names if
        not col.endswith('_var') and not col.startswith(('col_filler_', 'row_filler_')) and col != 'metric']
    if debug: print(col_names)
    col_names_for_grouping = col_names[:-1]
    use_groupby = bool(col_names_for_grouping)
    name_of_final_col = col_names[-1]  ## if nesting, the final col is the last / lowest one
    idx_of_final_col = var_names.index(name_of_final_col)
    vals_in_final_col = [list(inner_index)[idx_of_final_col] for inner_index in row_0.index]
    if debug: print(vals_in_final_col)
    has_total_col = TOTAL in vals_in_final_col  ## e.g. ['Chrome', 'Firefox', 'TOTAL']
    ## divide by 2 to handle doubling caused by inclusion of already-calculated value in TOTAL row in summing
    divide_by = 2 if has_total_col else 1
    index = list(df.index.names + var_names + ['n'])
    df_pre_pivot_inc_pct = pd.DataFrame(data=[], columns=index)  ## order doesn't matter - it will append based on col names, so both row % and col % work fine as long as original Freq df_pre_pivot comes first
    rounder = partial(_round_kws, dp=dp)
    for i, row in df.iterrows():
        ## do calculations
        if use_groupby:
            s_row_pcts = (100 * row) / (row.groupby(col_names_for_grouping).agg('sum') / divide_by)
        else:
            s_row_pcts = (100 * row) / (sum(row) / divide_by)
        s_row_pcts = s_row_pcts.apply(rounder)
        if debug: print(s_row_pcts)
        ## create rows ready to append to df_pre_pivot before re-pivoting but with additional metric type
        for sub_index, val in s_row_pcts.items():
            row_names = list(row.name) if is_cross_tab else [row.name]  ## e.g. ('Country', 'NZ', 'Gender', 'Female') vs 'Freq'
            values = row_names + list(sub_index) + [val]
            s = pd.Series(values, index=index)  ## order doesn't matter - see comment earlier
            s['metric'] = pct_type
            if debug: print(s)
            ## add to new df_pre_pivot
            df_pre_pivot_inc_pct = pd.concat([df_pre_pivot_inc_pct, s.to_frame().T])
    if debug: print(df_pre_pivot_inc_pct)
    return df_pre_pivot_inc_pct

def get_order_rules_for_multi_index_branches(row_specs: list[DimSpec], col_specs: list[DimSpec] | None = None) -> dict:
    """
    Should come from a GUI via an interface ad thence into the code using this.

    Note - to test Sort.INCREASING and Sort.DECREASING I'll need to manually check what expected results should be (groan)

    Note - because, below the top-level, only chains are allowed (not trees)
    the index for any variables after the first (top-level) are always 0.
    """
    orders = {}
    dims_type_specs = [row_specs, ]
    if col_specs:
        dims_type_specs.append(col_specs)
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
