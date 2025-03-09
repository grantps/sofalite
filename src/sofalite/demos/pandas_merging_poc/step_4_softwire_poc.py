"""
When creating SQL queries we need to use variable names.
When displaying results we will use (often different) variable labels, and also value labels.
When sorting items, we may need to sort by the cell contents themselves, but other times by something associated instead.
If we choose to sort by values, for example, we can't just sort of value labels.
We might want
< 20  [1]
20-29 [2]
...
rather than what we might get by sorting on the visible content.
Using VarLabels dcs makes this a lot easier to work with.

TODO: prevent reuse of same variables at top-level of rows or columns
Otherwise pandas merges them together (as you would expect given how JOIN is mean to work)
and everything is broken given we were trying to keep them separate.
"""
from collections.abc import Collection
from enum import StrEnum
from functools import cache
from itertools import combinations, count
from pathlib import Path
import sqlite3 as sqlite

import pandas as pd

from sofalite.conf.tables.misc import BLANK, TOTAL, Sort
from sofalite.demos.pandas_merging_poc.utils.html_fixes import (
    fix_top_left_box, merge_cols_of_blanks, merge_rows_of_blanks)
from sofalite.demos.pandas_merging_poc.utils.misc import apply_index_styles, display_tbl, set_table_styles
from sofalite.demos.pandas_merging_poc.utils.multi_index_sort import get_sorted_multi_index_list
from sofalite.utils.labels import yaml2varlabels

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1_000)

class PctType(StrEnum):
    ROW_PCT = 'Row %'
    COL_PCT = 'Col %'

yaml_fpath = Path(__file__).parent.parent.parent.parent.parent / 'store' / 'var_labels.yaml'
var_labels = yaml2varlabels(yaml_fpath,
    vars2include=['agegroup', 'browser', 'car', 'country', 'gender', 'home_country', 'std_agegroup'], debug=True)


class DataSpecificCheats:

    @staticmethod
    @cache
    def get_raw_df(*, debug=False) -> pd.DataFrame:
        con = sqlite.connect('sofa_db')
        cur = con.cursor()
        sql = """\
        SELECT id, agegroup, browser, car, agegroup as std_agegroup
        FROM demo_tbl
        """
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        con.close()
        df = pd.DataFrame(data, columns=['id', 'agegroup', 'browser', 'car', 'std_agegroup'])
        df['browser'] = df['browser'].apply(lambda s: 'Google Chrome' if s == 'Chrome' else s)  ## so we can apply Google Chrome as a label to prove labels work
        if debug:
            print(df)
        return df

    @staticmethod
    def get_orders_for_multi_index_branches() -> dict:
        """
        Should come from a GUI via an interface ad thence into the code using this.
        Note - to test Sort.INCREASING and Sort.DECREASING I'll need to manually check what expected results should be (groan)
        """
        return {
            ## columns
            ('agegroup', ): (0, Sort.VAL),
            ('browser', 'agegroup', ): (1, Sort.LBL, 0, Sort.VAL),
            ('std_agegroup', ): (2, Sort.VAL),
            ## rows
            ('country', 'gender', ): (0, Sort.VAL, 0, Sort.LBL),
            ('home_country', ): (1, Sort.LBL),
            ('car', ): (2, Sort.VAL),
        }


def get_df_pre_pivot_with_pcts(df: pd.DataFrame, *, pct_type: PctType, debug=False) -> pd.DataFrame:
    """
    Strategy - we have multi-indexes so let's use them!
    Note - exact same approach works if you work from the df (for rows and Row %) or from a transposed df (for cols and Col %)

browser_var                                                 Web Browser
browser                                                          Chrome                          Firefox                           Chrome   Firefox     TOTAL
agegroup_var                                                  Age Group                        Age Group                        Age Group Age Group Age Group
agegroup                                                           < 20 20-29 30-39 40-64  65+      < 20 20-29 30-39 40-64  65+     TOTAL     TOTAL      < 20 20-29 30-39 40-64  65+ TOTAL
measure                                                            Freq  Freq  Freq  Freq Freq      Freq  Freq  Freq  Freq Freq      Freq      Freq      Freq  Freq  Freq  Freq Freq  Freq
home_country_var home_country row_filler_var_0 row_filler_0
Home Country     NZ           __blank__        __blank__             18     8    10    27   30        35    25    24    51   55        93       190        53    33    34    78   85   283
             South Korea  __blank__        __blank__             32    17    16    35   21        49    23    17    43   49       121       181        81    40    33    78   70   302
             TOTAL        __blank__        __blank__             60    44    43    90   95       109    74    55   132  152       332       522       169   118    98   222  247   854
             USA          __blank__        __blank__             10    19    17    28   44        25    26    14    38   48       118       151        35    45    31    66   92   269

    Row %s are taken row (per column block e.g. Under Chrome, or under Firefox) per row.
    We have all the numbers we need so surely there must be some way to calculate it (spoiler - there is!).
    We can do it row by row if we have the information required available in the row. So do we? Let's look at a row:

    Each row is a Series with a multi-index on the left and the values on the right. E.g.:

    browser_var  browser  agegroup_var  agegroup  measure
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
    BUT with Row % or Col % as the measure not Freq.
    Note - OK if we don't include columns not used in pivot, and OK if the cols are not in the correct order.
    The appending is by col_name so it Just Works™ :-).
    Why? Because if we can get to that structure, we can just append the different dfs-by-measure together,
    and pivot the resulting combined df to get a column per measure.
    Trivial if we can get to that point - it Just Works™!
    """
    if pct_type == PctType.COL_PCT:
        df = df.T  ## if unpivoted, each row has values for the Row % calculation; otherwise has values for Col % calculation. If pivoted, it is the reverse. But still rows refers to rows and cols to cols in the df we're working through here either way.
    col_names = [col for col in df.columns.names if
        not col.endswith('_var') and not col.startswith(('col_filler_', 'row_filler_')) and col != 'measure']
    if debug: print(col_names)
    col_names_for_grouping = col_names[:-1]
    use_groupby = bool(col_names_for_grouping)
    ## divide by 2 to handle doubling caused by inclusion of already-calculated value in TOTAL row in summing
    name_of_final_col = col_names[-1]
    row_0 = df.iloc[0]
    var_names = row_0.index.names
    idx_of_final_col = var_names.index(name_of_final_col)
    vals_in_final_col = [list(inner_index)[idx_of_final_col] for inner_index in row_0.index]
    if debug: print(vals_in_final_col)
    has_total = TOTAL in vals_in_final_col
    divide_by = 2 if has_total else 1
    df_pre_pivot_inc_pct = pd.DataFrame(data=[], columns=list(df.index.names + var_names + ['n']))  ## order doesn't matter - it will append based on col names, so both row % and col % work fine as long as original Freq df_pre_pivot comes first
    for i, row in df.iterrows():
        ## do calculations
        if use_groupby:
            s_row_pcts = (100 * row) / (row.groupby(col_names_for_grouping).agg('sum') / divide_by)
        else:
            s_row_pcts = (100 * row) / (sum(row) / divide_by)
        if debug: print(s_row_pcts)
        ## create rows ready to append to df_pre_pivot before re-pivoting but with additional measure type
        for sub_index, val in s_row_pcts.items():
            values = list(row.name) + list(sub_index) + [val]
            s = pd.Series(values, index=list(df.index.names + var_names + ['n']))  ## order doesn't matter - see comment earlier
            s['measure'] = pct_type
            if debug: print(s)
            ## add to new df_pre_pivot
            df_pre_pivot_inc_pct = pd.concat([df_pre_pivot_inc_pct, s.to_frame().T])
    if debug: print(df_pre_pivot_inc_pct)
    return df_pre_pivot_inc_pct


def get_data_from_spec(all_variables: Collection[str], totalled_variables: Collection[str], filter: str,
        *, debug=False) -> list[list]:
    """
    TODO: change to a dc
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
    con = sqlite.connect('sofa_db')
    cur = con.cursor()
    tbl = 'demo_tbl'
    ## Step 0 - variable lists
    n_totalled = len(totalled_variables)
    ## Step 1 - group by all
    main_flds = ', '.join(all_variables)
    sql_main = f"""\
    SELECT {main_flds}, COUNT(*) AS n
    FROM {tbl}
    {filter}
    GROUP BY {main_flds}
    """
    cur.execute(sql_main)
    data.extend(cur.fetchall())
    ## Step 2 - combos
    totalled_combinations = []
    for n in count(1):
        totalled_combinations_for_n = combinations(totalled_variables, n)
        totalled_combinations.extend(totalled_combinations_for_n)
        if n == n_totalled:
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
        FROM {tbl}
        {filter}
        {group_by}
        """
        if debug: print(f"sql_totalled={sql_totalled}")
        cur.execute(sql_totalled)
        data.extend(cur.fetchall())
    if debug:
        for row in data:
            print(row)
    return data


class GetData:

    """
    Filtering some values to reduce the sheer size of the table so it is easier to see at once.
    Thus, the filter clause: WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari').
    Top, middle, and bottom must share same column variables.
    Left and right must share same row variables.
    """

    ## TOP df **********************************************************************************************************

    ## TOP LEFT & RIGHT (reused to put more strain on row-spanning of columns and reuse of column names)
    @staticmethod
    def get_country_gender_by_age_group(*, debug=False) -> pd.DataFrame:
        """
        Wipe out agegroup 4 in the source data to confirm the combined table output
        has agegroup 4 column anyway because it is in the country row table.

        Needs two level column dimension columns because left df has two column dimension levels
        i.e. browser and agegroup. So dummy variable needed.

        LEFT has two levels:

        browser    Chrome                        Firefox
        agegroup   <20 20-29 30-39 40-64 65+     <20 20-29 30-39 40-64 65+

        so RIGHT needs two as well (so dummy filler needed):

        agegroup  <20 20-29 30-39 65+
        dummy
        """
        all_variables = ['country', 'gender', 'agegroup']
        totalled_variables = ['country', 'gender', 'agegroup']
        filter = """\
        WHERE agegroup <> 4
        AND browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        """
        data = get_data_from_spec(all_variables=all_variables, totalled_variables=totalled_variables, filter=filter, debug=debug)

        country_val_labels = var_labels.var2var_label_spec['country']
        gender_val_labels = var_labels.var2var_label_spec['gender']
        agegroup_val_labels = var_labels.var2var_label_spec['agegroup']

        df_pre_pivot = pd.DataFrame(data,
            columns=[country_val_labels.pandas_val, gender_val_labels.pandas_val, agegroup_val_labels.pandas_val, 'n'])
        df_pre_pivot[country_val_labels.pandas_var] = country_val_labels.lbl
        df_pre_pivot[country_val_labels.name] = df_pre_pivot[country_val_labels.pandas_val].apply(lambda x: country_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot[gender_val_labels.pandas_var] = gender_val_labels.lbl
        df_pre_pivot[gender_val_labels.name] = df_pre_pivot[gender_val_labels.pandas_val].apply(lambda x: gender_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot[agegroup_val_labels.pandas_var] = agegroup_val_labels.lbl
        df_pre_pivot[agegroup_val_labels.name] = df_pre_pivot[agegroup_val_labels.pandas_val].apply(lambda x: agegroup_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot['col_filler_var_0'] = BLANK
        df_pre_pivot['col_filler_0'] = BLANK  ## add filler column which we'll nest under age_group as natural outcome of pivot step
        df_pre_pivot['measure'] = 'Freq'
        print(df_pre_pivot)
        df = (df_pre_pivot
            .pivot(
                index=[country_val_labels.pandas_var, country_val_labels.name, gender_val_labels.pandas_var, gender_val_labels.name],
                columns=[agegroup_val_labels.pandas_var, agegroup_val_labels.name, 'col_filler_var_0', 'col_filler_0', 'measure'],
                values='n')
        )
        if debug: print(f"\nTOP LEFT & RIGHT:\n{df}")
        return df

    ## TOP MIDDLE
    @staticmethod
    def get_country_gender_by_browser_and_age_group(*, debug=False) -> pd.DataFrame:
        """
        Special step to test whether this merging approach works correctly
        when some value combinations are empty in one block but not in another.
        Wipe out gender 1 from country 3 in the source data to confirm that the final combined table output
        has gender 1 from country 3 anyway because it is in the agegroup table.

        Warning - NO MALES IN NZ! ;-)

        Note - when multi-level, every column is a tuple e.g. a row dimension column (once index reset)
        might be ('country', '') and a column dimension column ('Firefox', '20-29').
        There will be empty string items padding out row dimension columns so that there will be as many
        tuple items as column dimension levels.

        GET RAW DATA

            country  gender  browser age_group   n
        0         1       1   Chrome       <20   7
        1         1       1   Chrome     20-29  13
        ...
        5         1       1  Firefox       <20  12
        ...
        10        1       2   Chrome       <20   3

        ADD LABELLED CATEGORY COLS AND VAL COLS

            country_var  country  gender_var  gender   browser_var  browser  age_group_var  age_group   n
        0             1       NZ           1    Male        Chrome   Chrome              1        <20   7
        1             1       NZ           1    Male        Chrome   Chrome              2      20-29  13
        ...
        5             1       NZ           1    Male       Firefox  Firefox              1        <20  12
        ...
        10            1       NZ           2  Female        Chrome   Chrome              1        <20   3

        PIVOT so ['country', 'gender'] => rows, and ['browser', 'age_group'] => columns

                   row 0      row 1
                     |          |
                     |          |
        col 0 -->  browser      |      |  Chrome                        Firefox
        col 1 -->  age_group    |      |  <20 20-29 30-39 40-64 65+     <20 20-29 30-39 40-64 65+
        -------------------------------|--------------------------------------------------------
                     |          |
                     V          V
                   country     gender  |
                   NZ          Female  |   3     6     5    11  19      13    10     6    22  20
                               Male    |   7    13    12    17  25      12    16     8    16  28
                   South Korea Female  |  14     7     5    12  10      27    16     8    18  21
                               Male    |  18    10    11    23  11      22     7     9    25  28
                   U.S.A       Female  |   7     4     5    16  15      18    14     8    28  31

        Note - working with indexes not data values until final flattening step
        """
        all_variables = ['country', 'gender', 'browser', 'agegroup']
        totalled_variables = ['country', 'gender', 'browser', 'agegroup']
        filter = """\
        WHERE NOT (country = 3 AND gender = 1)
        AND browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        """
        data = get_data_from_spec(all_variables=all_variables, totalled_variables=totalled_variables, filter=filter, debug=debug)

        country_val_labels = var_labels.var2var_label_spec['country']
        browser_val_labels = var_labels.var2var_label_spec['browser']
        gender_val_labels = var_labels.var2var_label_spec['gender']
        agegroup_val_labels = var_labels.var2var_label_spec['agegroup']

        df_pre_pivot = pd.DataFrame(data, columns=[country_val_labels.pandas_val, gender_val_labels.pandas_val,
            browser_val_labels.pandas_val, agegroup_val_labels.pandas_val, 'n'])
        df_pre_pivot[country_val_labels.pandas_var] = country_val_labels.lbl
        df_pre_pivot[country_val_labels.name] = df_pre_pivot[country_val_labels.pandas_val].apply(lambda x: country_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot[gender_val_labels.pandas_var] = gender_val_labels.lbl
        df_pre_pivot[gender_val_labels.name] = df_pre_pivot[gender_val_labels.pandas_val].apply(lambda x: gender_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot[browser_val_labels.pandas_var] = browser_val_labels.lbl
        df_pre_pivot[browser_val_labels.name] = df_pre_pivot[browser_val_labels.pandas_val].apply(lambda x: browser_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot[agegroup_val_labels.pandas_var] = agegroup_val_labels.lbl
        df_pre_pivot[agegroup_val_labels.name] = df_pre_pivot[agegroup_val_labels.pandas_val].apply(lambda x: agegroup_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot['measure'] = 'Freq'

        df = (df_pre_pivot
            .pivot(
                index=[country_val_labels.pandas_var, country_val_labels.name, gender_val_labels.pandas_var, gender_val_labels.name],
                columns=[browser_val_labels.pandas_var, browser_val_labels.name, agegroup_val_labels.pandas_var, agegroup_val_labels.name, 'measure'],
                values='n')
        )

        df_pre_pivot_inc_row_pct = get_df_pre_pivot_with_pcts(df, pct_type=PctType.ROW_PCT, debug=debug)
        df_pre_pivot_inc_col_pct = get_df_pre_pivot_with_pcts(df, pct_type=PctType.COL_PCT, debug=debug)
        df_pre_pivot = pd.concat([df_pre_pivot, df_pre_pivot_inc_row_pct, df_pre_pivot_inc_col_pct])
        df = (df_pre_pivot.pivot(
                index=[country_val_labels.pandas_var, country_val_labels.name, gender_val_labels.pandas_var, gender_val_labels.name],
                columns=[browser_val_labels.pandas_var, browser_val_labels.name, agegroup_val_labels.pandas_var, agegroup_val_labels.name, 'measure'],
                values='n')
        )

        if debug: print(f"\nTOP MIDDLE:\n{df}")
        return df

    ## MIDDLE df *******************************************************************************************************

    """
    Note - must have same columns for left as for TOP left df, for middle as TOP middle df,
    and for the right as for TOP right df
    Note - can't have country twice at top-level but OK if different variable name.
    """

    ## MIDDLE LEFT & RIGHT
    @staticmethod
    def get_country_by_age_group(*, debug=False) -> pd.DataFrame:
        """
        Needs two level column dimension columns because left df has two column dimension levels
        i.e. browser and age_group. So filler variable needed.
        """
        all_variables = ['country', 'agegroup']
        totalled_variables = ['country', 'agegroup']
        filter = """\
        WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        """
        data = get_data_from_spec(all_variables=all_variables, totalled_variables=totalled_variables, filter=filter, debug=debug)

        country_val_labels = var_labels.var2var_label_spec['home_country']
        agegroup_val_labels = var_labels.var2var_label_spec['agegroup']

        df_pre_pivot = pd.DataFrame(data, columns=[country_val_labels.pandas_val, agegroup_val_labels.pandas_val, 'n'])
        df_pre_pivot[country_val_labels.pandas_var] = country_val_labels.lbl
        df_pre_pivot[country_val_labels.name] = df_pre_pivot[country_val_labels.pandas_val].apply(lambda x: country_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot['row_filler_var_0'] = BLANK
        df_pre_pivot['row_filler_0'] = BLANK
        df_pre_pivot[agegroup_val_labels.pandas_var] = agegroup_val_labels.lbl
        df_pre_pivot[agegroup_val_labels.name] = df_pre_pivot[agegroup_val_labels.pandas_val].apply(lambda x: agegroup_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot['col_filler_var_0'] = BLANK
        df_pre_pivot['col_filler_0'] = BLANK
        df_pre_pivot['measure'] = 'Freq'
        df = (df_pre_pivot
            .pivot(
                index=[country_val_labels.pandas_var, country_val_labels.name, 'row_filler_var_0', 'row_filler_0'],
                columns=[agegroup_val_labels.pandas_var, agegroup_val_labels.name, 'col_filler_var_0', 'col_filler_0', 'measure'],
                values='n')
        )
        if debug: print(f"\nMIDDLE LEFT & RIGHT:\n{df}")
        return df

    ## MIDDLE MIDDLE
    @staticmethod
    def get_country_by_browser_and_age_group(*, debug=False) -> pd.DataFrame:  ## TODO: automate and soft-wire this splaying and gathering
        all_variables = ['country', 'browser', 'agegroup']
        totalled_variables = ['country', 'browser', 'agegroup']
        filter = """\
        WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        """
        data = get_data_from_spec(all_variables=all_variables, totalled_variables=totalled_variables, filter=filter, debug=debug)

        country_val_labels = var_labels.var2var_label_spec['home_country']
        browser_val_labels = var_labels.var2var_label_spec['browser']
        agegroup_val_labels = var_labels.var2var_label_spec['agegroup']

        df_pre_pivot = pd.DataFrame(data, columns=[country_val_labels.pandas_val, browser_val_labels.pandas_val, agegroup_val_labels.pandas_val, 'n'])
        df_pre_pivot[country_val_labels.pandas_var] = country_val_labels.lbl
        df_pre_pivot[country_val_labels.name] = df_pre_pivot[country_val_labels.pandas_val].apply(lambda x: country_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot['row_filler_var_0'] = BLANK
        df_pre_pivot['row_filler_0'] = BLANK
        df_pre_pivot[browser_val_labels.pandas_var] = browser_val_labels.lbl
        df_pre_pivot[browser_val_labels.name] = df_pre_pivot[browser_val_labels.pandas_val].apply(lambda x: browser_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot[agegroup_val_labels.pandas_var] = agegroup_val_labels.lbl
        df_pre_pivot[agegroup_val_labels.name] = df_pre_pivot[agegroup_val_labels.pandas_val].apply(lambda x: agegroup_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot['measure'] = 'Freq'
        df = (df_pre_pivot
            .pivot(
                index=[country_val_labels.pandas_var, country_val_labels.name, 'row_filler_var_0', 'row_filler_0'],
                columns=[browser_val_labels.pandas_var, browser_val_labels.name, agegroup_val_labels.pandas_var, agegroup_val_labels.name, 'measure'],
                values='n')
        )

        df_pre_pivot_inc_row_pct = get_df_pre_pivot_with_pcts(df, pct_type=PctType.ROW_PCT, debug=debug)
        df_pre_pivot_inc_col_pct = get_df_pre_pivot_with_pcts(df, pct_type=PctType.COL_PCT, debug=debug)
        df_pre_pivot = pd.concat([df_pre_pivot, df_pre_pivot_inc_row_pct, df_pre_pivot_inc_col_pct])
        df = (df_pre_pivot.pivot(
                index=[country_val_labels.pandas_var, country_val_labels.name, 'row_filler_var_0', 'row_filler_0'],
                columns=[browser_val_labels.pandas_var, browser_val_labels.name, agegroup_val_labels.pandas_var, agegroup_val_labels.name, 'measure'],
                values='n')
        )
        if debug: print(f"\nMIDDLE MIDDLE:\n{df}")
        return df

    ## BOTTOM df *******************************************************************************************************

    """
    Note - must have same columns for left as for TOP left df and for the right as for TOP right df
    """

    ## BOTTOM LEFT & RIGHT
    @staticmethod
    def get_car_by_age_group(*, debug=False) -> pd.DataFrame:
        """
        Needs two level column dimension columns because left df has two column dimension levels
        i.e. browser and age_group. So filler variable needed.
        """
        all_variables = ['car', 'agegroup']
        totalled_variables = ['agegroup']
        filter = """\
        WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        AND car IN (2, 3, 11)
        """
        data = get_data_from_spec(all_variables=all_variables, totalled_variables=totalled_variables, filter=filter, debug=debug)

        car_val_labels = var_labels.var2var_label_spec['car']
        agegroup_val_labels = var_labels.var2var_label_spec['agegroup']

        df_pre_pivot = pd.DataFrame(data, columns=[car_val_labels.pandas_val, agegroup_val_labels.pandas_val, 'n'])
        df_pre_pivot[car_val_labels.pandas_var] = car_val_labels.lbl
        df_pre_pivot[car_val_labels.name] = df_pre_pivot[car_val_labels.pandas_val].apply(lambda x: car_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot['row_filler_var_0'] = BLANK
        df_pre_pivot['row_filler_0'] = BLANK
        df_pre_pivot[agegroup_val_labels.pandas_var] = agegroup_val_labels.lbl
        df_pre_pivot[agegroup_val_labels.name] = df_pre_pivot[agegroup_val_labels.pandas_val].apply(lambda x: agegroup_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot['col_filler_var_0'] = BLANK
        df_pre_pivot['col_filler_0'] = BLANK
        df_pre_pivot['measure'] = 'Freq'
        df = (df_pre_pivot
            .pivot(
                index=[car_val_labels.pandas_var, car_val_labels.name, 'row_filler_var_0', 'row_filler_0'],
                columns=[agegroup_val_labels.pandas_var, agegroup_val_labels.name, 'col_filler_var_0', 'col_filler_0', 'measure'],
                values='n')
        )
        if debug: print(f"\nBOTTOM LEFT & RIGHT:\n{df}")
        return df

    ## BOTTOM MIDDLE
    @staticmethod
    def get_car_by_browser_and_age_group(*, debug=False) -> pd.DataFrame:
        all_variables = ['car', 'browser', 'agegroup']
        totalled_variables = ['browser', 'agegroup']
        filter = """\
        WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        AND car IN (2, 3, 11)
        """
        data = get_data_from_spec(all_variables=all_variables, totalled_variables=totalled_variables, filter=filter, debug=debug)

        car_val_labels = var_labels.var2var_label_spec['car']
        browser_val_labels = var_labels.var2var_label_spec['browser']
        agegroup_val_labels = var_labels.var2var_label_spec['agegroup']

        df_pre_pivot = pd.DataFrame(data, columns=[car_val_labels.pandas_val, browser_val_labels.pandas_val, agegroup_val_labels.pandas_val, 'n'])
        df_pre_pivot[car_val_labels.pandas_var] = car_val_labels.lbl
        df_pre_pivot[car_val_labels.name] = df_pre_pivot[car_val_labels.pandas_val].apply(lambda x: car_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot['row_filler_var_0'] = BLANK
        df_pre_pivot['row_filler_0'] = BLANK
        df_pre_pivot[browser_val_labels.pandas_var] = browser_val_labels.lbl
        df_pre_pivot[browser_val_labels.name] = df_pre_pivot[browser_val_labels.pandas_val].apply(lambda x: browser_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot[agegroup_val_labels.pandas_var] = agegroup_val_labels.lbl
        df_pre_pivot[agegroup_val_labels.name] = df_pre_pivot[agegroup_val_labels.pandas_val].apply(lambda x: agegroup_val_labels.val2lbl.get(x, str(x)))
        df_pre_pivot['measure'] = 'Freq'
        df = (df_pre_pivot
            .pivot(
                index=[car_val_labels.pandas_var, car_val_labels.name, 'row_filler_var_0', 'row_filler_0'],
                columns=[browser_val_labels.pandas_var, browser_val_labels.name, agegroup_val_labels.pandas_var, agegroup_val_labels.name, 'measure'],
                values='n')
        )
        df_pre_pivot_inc_row_pct = get_df_pre_pivot_with_pcts(df, pct_type=PctType.ROW_PCT, debug=debug)
        df_pre_pivot_inc_col_pct = get_df_pre_pivot_with_pcts(df, pct_type=PctType.COL_PCT, debug=debug)
        df_pre_pivot = pd.concat([df_pre_pivot, df_pre_pivot_inc_row_pct, df_pre_pivot_inc_col_pct])
        df = (df_pre_pivot
            .pivot(
                index=[car_val_labels.pandas_var, car_val_labels.name, 'row_filler_var_0', 'row_filler_0'],
                columns=[browser_val_labels.pandas_var, browser_val_labels.name, agegroup_val_labels.pandas_var, agegroup_val_labels.name, 'measure'],
                values='n')
        )
        if debug: print(f"\nBOTTOM MIDDLE:\n{df}")
        return df


## COMBINED - TOP + BOTTOM

def get_step_1_tbl_df(*, debug=False) -> pd.DataFrame:
    """
    Note - using pd.concat or df.merge(how='outer') has the same result but I use merge for horizontal joining
    to avoid repeating the row dimension columns e.g. country and gender.

    Basically we are merging left and right dfs. Merging is typically on an id field that both parts share.
    In this case there are as many fields to merge on as there are fields in the row index -
    in this example there are 4 (var_00, val_00, var_01, and val_01).
    There is one added complexity because the column is multi-index.
    We need to supply a tuple with an item (possibly an empty string) for each level.
    In this case there are two levels (browser and age_group). So we merge on
    [('var_00', ''), ('val_00', ''), ('var_01', ''), ('val_01', '')]
    If there were three row levels and four col levels we would need something like:
    [('var_00', '', '', ''), ('val_00', '', '', ''), ... ('val_02', '', '', '')]

    BOTTOM LEFT:
    browser    var_00       val_00     var_01     val_01 Chrome                       Firefox
    agegroup                                                <20 20-29 30-39 40-64 65+     <20 20-29 30-39 40-64 65+
    0         Country           NZ  __blank__  __blank__     10    19    17    28  44      25    26    14    38  48
    ...

    BOTTOM RIGHT:
    agegroup   var_00       val_00     var_01     val_01 <20 20-29 30-39 40-64 65+
    dummy
    0         Country           NZ  __blank__  __blank__  35    45    31    66  92
    ...

    Note - we flatten out the row multi-index using reset_index().
    This flattening results in a column per row variable e.g. one for country and one for gender
     (at this point we're ignoring the labelling step where we split each row variable e.g. for country into Country (var) and NZ (val)).
    Given it is a column, it has to have as many levels as the column dimension columns.
    So if there are two column dimension levels each row column will need to be a two-tuple e.g. ('gender', '').
    If there were three column dimension levels the row column would need to be a three-tuple e.g. ('gender', '', '').
    """
    agegroup_val_labels = var_labels.var2var_label_spec['agegroup']
    car_val_labels = var_labels.var2var_label_spec['car']
    country_val_labels = var_labels.var2var_label_spec['country']
    gender_val_labels = var_labels.var2var_label_spec['gender']
    home_country_val_labels = var_labels.var2var_label_spec['home_country']
    ## TOP
    df_top_left = GetData.get_country_gender_by_age_group(debug=debug)
    df_top_right = GetData.get_country_gender_by_browser_and_age_group(debug=debug)
    df_top = df_top_left.merge(df_top_right, how='outer', on=[country_val_labels.pandas_var, country_val_labels.name, gender_val_labels.pandas_var, gender_val_labels.name])
    df_top_repeat = df_top_left.copy()
    df_top_repeat.rename(columns={agegroup_val_labels.lbl: 'Std Age Group'}, inplace=True)  ## as if there were a real variable - but we'll need to add that fake variable to the VarLabels we use
    df_top = df_top.merge(df_top_repeat, how='outer', on=[country_val_labels.pandas_var, country_val_labels.name, gender_val_labels.pandas_var, gender_val_labels.name])  ## join again to test ability to  handle col-spanning offsets etc
    ## MIDDLE
    df_middle_left = GetData.get_country_by_age_group(debug=debug)
    df_middle_right = GetData.get_country_by_browser_and_age_group(debug=debug)
    df_middle = df_middle_left.merge(df_middle_right, how='outer', on=[home_country_val_labels.pandas_var, home_country_val_labels.name, 'row_filler_var_0', 'row_filler_0'])
    df_middle_repeat = df_middle_left.copy()
    df_middle_repeat.rename(columns={agegroup_val_labels.lbl: 'Std Age Group'}, inplace=True)
    df_middle = df_middle.merge(df_middle_repeat, how='outer', on=[home_country_val_labels.pandas_var, home_country_val_labels.name, 'row_filler_var_0', 'row_filler_0'])
    ## BOTTOM
    df_bottom_left = GetData.get_car_by_age_group(debug=debug)
    df_bottom_right = GetData.get_car_by_browser_and_age_group(debug=debug)
    df_bottom = df_bottom_left.merge(df_bottom_right, how='outer', on=[car_val_labels.pandas_var, car_val_labels.name, 'row_filler_var_0', 'row_filler_0'])
    df_bottom_repeat = df_bottom_left.copy()
    df_bottom_repeat.rename(columns={agegroup_val_labels.lbl: 'Std Age Group'}, inplace=True)
    df_bottom = df_bottom.merge(df_bottom_repeat, how='outer', on=[car_val_labels.pandas_var, car_val_labels.name, 'row_filler_var_0', 'row_filler_0'])
    if debug:
        print(f"\nTOP:\n{df_top}\n\nMIDDLE:\n{df_middle}\n\nBOTTOM:\n{df_bottom}")
    ## COMBINE using pandas JOINing (the big magic trick at the middle of this approach to complex table-making)
    ## Unfortunately, delegating to Pandas means we can't fix anything intrinsic to what Pandas does - and there is a bug (from my point of view)
    ## whenever tables are merged with the same variables at the top level. To prevent this we have to disallow variable re-use at top-level.
    ## transpose, join, and re-transpose back. JOINing on rows works differently from columns and will include all items in sub-levels under the correct upper levels even if missing from the first multi-index
    ## E.g. if Age Group > 40-64 is missing from the first index it will not be appended on the end but will be alongside all its siblings so we end up with Age Group > >20, 20-29 30-39, 40-64, 65+
    ## Note - variable levels (odd numbered levels if 1 is the top level) should be in the same order as they were originally
    df_t = df_top.T.join(df_middle.T, how='outer')
    df_t = df_t.join(df_bottom.T, how='outer')
    df = df_t.T  ## re-transpose back so cols are cols and rows are rows again
    df.fillna(0, inplace=True)
    if debug: print(f"\nCOMBINED:\n{df}")
    ## Sorting indexes
    raw_df = DataSpecificCheats.get_raw_df(debug=debug)
    orders_for_multi_index_branches = DataSpecificCheats.get_orders_for_multi_index_branches()
    ## COLS
    unsorted_col_multi_index_list = list(df.columns)
    sorted_col_multi_index_list = get_sorted_multi_index_list(
        unsorted_col_multi_index_list, orders_for_multi_index_branches=orders_for_multi_index_branches,
        var_lbl2var=var_labels.var_lbl2var, var_and_val_lbl2val=var_labels.var_and_val_lbl2val,
        raw_df=raw_df, has_metrics=True, debug=debug)
    sorted_col_multi_index = pd.MultiIndex.from_tuples(sorted_col_multi_index_list)  ## https://pandas.pydata.org/docs/user_guide/advanced.html
    ## ROWS
    unsorted_row_multi_index_list = list(df.index)
    sorted_row_multi_index_list = get_sorted_multi_index_list(
        unsorted_row_multi_index_list, orders_for_multi_index_branches=orders_for_multi_index_branches,
        var_lbl2var=var_labels.var_lbl2var, var_and_val_lbl2val=var_labels.var_and_val_lbl2val,
        raw_df=raw_df, has_metrics=False, debug=debug)
    sorted_row_multi_index = pd.MultiIndex.from_tuples(sorted_row_multi_index_list)  ## https://pandas.pydata.org/docs/user_guide/advanced.html
    df = df.reindex(index=sorted_row_multi_index, columns=sorted_col_multi_index)
    if debug: print(f"\nORDERED:\n{df}")
    return df

def main(*, debug=False, verbose=False):
    df = get_step_1_tbl_df(debug=True)
    style_name = 'prestige_screen'
    pd_styler = set_table_styles(df.style)
    pd_styler = apply_index_styles(df, style_name, pd_styler, axis='rows')
    pd_styler = apply_index_styles(df, style_name, pd_styler, axis='columns')
    raw_tbl_html = pd_styler.to_html()
    if debug:
        print(raw_tbl_html)
    ## Fix
    tbl_html = raw_tbl_html
    tbl_html = fix_top_left_box(tbl_html, style_name, debug=debug, verbose=verbose)
    tbl_html = merge_cols_of_blanks(tbl_html, debug=debug)
    tbl_html = merge_rows_of_blanks(tbl_html, debug=debug, verbose=verbose)
    if debug:
        print(pd_styler.uuid)
        print(tbl_html)
    display_tbl(tbl_html, 'step_1_from_real_data', style_name)

if __name__ == '__main__':
    """
    TODO: Redo the fixing and merging so it works with new inputs
    """
    pass
    # df_top_right = GetData.get_country_gender_by_browser_and_age_group(debug=True)
    main(debug=True, verbose=False)
    # all_variables = ['country', 'gender', 'agegroup']
    # totalled_variables = ['country', 'gender', 'agegroup']
    # filter = """\
    #     WHERE agegroup <> 4
    #     AND browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
    #     """
    # data = get_data_from_spec(
    #     all_variables=all_variables, totalled_variables=totalled_variables, filter=filter, debug=True)
