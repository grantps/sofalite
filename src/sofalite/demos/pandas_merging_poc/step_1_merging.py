"""
TODO: cope with location of 40-64 columns because missing in top so stuck on end by pandas
Have to work out what is going to be in the columns later? Damn! I want Pandas to take care of all that properly by itself.

Target Table
============

Example of real df (with different but similar structure) ready to make into HTML table (proven to work already in demo_tables.py)
Below is from pd.MultiIndex.from_tuples

                                    Age Group                                                                                     ... Web Browser
                                         < 20                      20-29                 30-39                 40-64              ...     Firefox              Internet Explorer              Opera              Safari
                                    __blank__                  __blank__             __blank__             __blank__              ...         Car                            Car                Car                 Car
                                    __blank__                  __blank__             __blank__             __blank__              ...         BMW Porsche Audi               BMW Porsche Audi   BMW Porsche Audi    BMW Porsche Audi
                                         Freq      Col % Row %      Freq Col % Row %      Freq Col % Row %      Freq Col % Row %  ...        Freq    Freq Freq              Freq    Freq Freq  Freq    Freq Freq   Freq    Freq Freq
Country Japan   Gender    Male              4  50.000000  11.8         6  66.7  17.6         4  36.4  11.8        11  61.1  32.4  ...           7       0    2                 1       1    6     1       0    1      1       0    2
                          Female            4  50.000000  12.9         3  33.3   9.7         7  63.6  22.6         7  38.9  22.6  ...           4       3    3                 3       2    1     1       2    1      1       1    0
        Italy   Gender    Male             10  66.700000  34.5         2  33.3   6.9         3  37.5  10.3         8  47.1  27.6  ...           7       3    2                 4       1    0     2       1    0      2       1    0
                          Female            5  33.333333  16.7         4  66.7  13.3         5  62.5  16.7         9  52.9  30.0  ...           6       3    1                 2       1    2     0       0    0      6       0    3
        Germany Gender    Male             15  39.500000  17.0        12  46.2  13.6        16  64.0  18.2        24  50.0  27.3  ...          13       6   13                 9       4    8     4       0    4      3       3    4
                          Female           23  60.500000  22.8        14  53.8  13.9         9  36.0   8.9        24  50.0  23.8  ...          13       5   16                 9       7    4     6       1    6      6       2    6
Gender  Male    __blank__ __blank__        29  47.500000  19.2        20  48.8  13.2        23  52.3  15.2        43  51.8  28.5  ...          27       9   17                14       6   14     7       1    5      6       4    6
        Female  __blank__ __blank__        32  52.500000  19.8        21  51.2  13.0        21  47.7  13.0        40  48.2  24.7  ...          23      11   20                14      10    7     7       3    7     13       3    9


Actual table made in this step from real data:

                                              Browser                                                           Age Group
                                               Chrome                           Firefox                               <20     20-29     30-39       65+     40-64
                                            Age Group                         Age Group                         __blank__ __blank__ __blank__ __blank__ __blank__
                                                  <20 20-29 30-39 40-64   65+       <20 20-29 30-39 40-64   65+ __blank__ __blank__ __blank__ __blank__ __blank__
measure                                          Freq  Freq  Freq  Freq  Freq      Freq  Freq  Freq  Freq  Freq      Freq      Freq      Freq      Freq      Freq
country_var country
Country     NZ          Gender    Female          3.0   6.0   5.0  11.0  19.0      13.0  10.0   6.0  22.0  20.0        16        16        11        39       0.0
                                  Male            7.0  13.0  12.0  17.0  25.0      12.0  16.0   8.0  16.0  28.0        19        29        20        53       0.0
            South Korea Gender    Female         14.0   7.0   5.0  12.0  10.0      27.0  16.0   8.0  18.0  21.0        41        23        13        31       0.0
                                  Male           18.0  10.0  11.0  23.0  11.0      22.0   7.0   9.0  25.0  28.0        40        17        20        39       0.0
            U.S.A       Gender    Female          7.0   4.0   5.0  16.0  15.0      18.0  14.0   8.0  28.0  31.0        25        18        13        46       0.0
                                  Male            0.0   0.0   0.0   0.0   0.0       0.0   0.0   0.0   0.0   0.0        28        15        21        39       0.0
            NZ          __blank__ __blank__      10.0  19.0  17.0  28.0  44.0      25.0  26.0  14.0  38.0  48.0        35        45        31        92      66.0
            South Korea __blank__ __blank__      32.0  17.0  16.0  35.0  21.0      49.0  23.0  17.0  43.0  49.0        81        40        33        70      78.0
            U.S.A       __blank__ __blank__      18.0   8.0  10.0  27.0  30.0      35.0  25.0  24.0  51.0  55.0        53        33        34        85      78.0

Notes on Target Table
=====================

Divides into 4 sub-blocks:
* top-left: country > gender vs browser > age_group
* bottom-left: country vs browser > age_group
* top-right: country > gender vs age_group
* bottom-right: country vs age_group

We consolidate into one table in two steps:
* consolidate into top and bottom
* consolidate into single table

Challenges
----------

Nested levels / multi-indexes:

e.g. country > gender

Different indexes:

e.g. country > gender on top and just country below

Implication: need to have blank placeholders in some blocks to enable consolidation with other blocks.
In the example above, the bottom-right block only needs country vs age_group for itself,
but needs country > placeholder vs age_group > placeholder to enable it to merge with the other blocks.

Note - use multi-indexes in df wherever more than one level. Note if a block from any direction has more levels than us
we'll need to extend to match so we can all be combined
"""

import pandas as pd
import sqlite3 as sqlite

from sofalite.conf.tables.misc import BLANK
from sofalite.demos.pandas_merging_poc.utils.misc import (
    apply_index_styles, columns_multi_index_fixer, display_tbl, set_table_styles)
from sofalite.demos.pandas_merging_poc.utils.html_fixes import (
    fix_top_left_box, merge_cols_of_blanks, merge_rows_of_blanks)

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 500)

age_group_map = {1: '<20', 2: '20-29', 3: '30-39', 4: '40-64', 5: '65+'}
car_map = {2: 'Porsche', 3: 'Audi'}
country_map = {1: 'NZ', 2: 'South Korea', 3: 'U.S.A'}
gender_map = {1: 'Male', 2: 'Female'}


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
        con = sqlite.connect('sofa_db')
        cur = con.cursor()
        sql = """\
        SELECT country, gender, agegroup, COUNT(*) AS n
        FROM demo_tbl
        WHERE agegroup <> 4 
        AND browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        GROUP BY country, gender, agegroup
        """
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        con.close()
        df_pre_pivot = pd.DataFrame(data, columns=['country_val', 'gender_val', 'age_group_val', 'n'])
        df_pre_pivot['country_var'] = 'Country'
        df_pre_pivot['country'] = df_pre_pivot['country_val'].apply(lambda x: country_map[x])
        df_pre_pivot['gender_var'] = 'Gender'
        df_pre_pivot['gender'] = df_pre_pivot['gender_val'].apply(lambda x: gender_map[x])
        df_pre_pivot['age_group_var'] = 'Age Group'
        df_pre_pivot['age_group'] = df_pre_pivot['age_group_val'].apply(lambda x: age_group_map[x])
        df_pre_pivot['col_filler_var_0'] = BLANK
        df_pre_pivot['col_filler_0'] = BLANK  ## add filler column which we'll nest under age_group as natural outcome of pivot step
        df_pre_pivot['measure'] = 'Freq'
        df = (df_pre_pivot
            .pivot(
                index=['country_var', 'country', 'gender_var', 'gender'],
                columns=['age_group_var', 'age_group', 'col_filler_var_0', 'col_filler_0', 'measure'],
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
        con = sqlite.connect('sofa_db')
        cur = con.cursor()
        sql = """\
        SELECT country, gender, browser, agegroup, COUNT(*) AS n
        FROM demo_tbl
        WHERE NOT (country = 3 AND gender = 1)
        AND browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        GROUP BY country, gender, browser, agegroup
        """
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        con.close()
        df_pre_pivot = pd.DataFrame(data, columns=['country_val', 'gender_val', 'browser_val', 'age_group_val', 'n'])
        df_pre_pivot['country_var'] = 'Country'
        df_pre_pivot['country'] = df_pre_pivot['country_val'].apply(lambda x: country_map[x])
        df_pre_pivot['gender_var'] = 'Gender'
        df_pre_pivot['gender'] = df_pre_pivot['gender_val'].apply(lambda x: gender_map[x])
        df_pre_pivot['browser_var'] = 'Browser'
        df_pre_pivot['browser'] = df_pre_pivot['browser_val']
        df_pre_pivot['age_group_var'] = 'Age Group'
        df_pre_pivot['age_group'] = df_pre_pivot['age_group_val'].apply(lambda x: age_group_map[x])
        df_pre_pivot['measure'] = 'Freq'
        df = (df_pre_pivot
            .pivot(
                index=['country_var', 'country', 'gender_var', 'gender'],
                columns=['browser_var', 'browser', 'age_group_var', 'age_group', 'measure'],
                values='n')
        )
        if debug: print(f"\nTOP MIDDLE:\n{df}")
        return df

    ## MIDDLE df *******************************************************************************************************

    """
    Note - must have same columns for left as for TOP left df, for middle as TOP middle df,
    and for the right as for TOP right df
    """

    ## MIDDLE LEFT & RIGHT
    @staticmethod
    def get_country_by_age_group(*, debug=False) -> pd.DataFrame:
        """
        Needs two level column dimension columns because left df has two column dimension levels
        i.e. browser and age_group. So filler variable needed.
        """
        con = sqlite.connect('sofa_db')
        cur = con.cursor()
        sql = """\
        SELECT country, agegroup, COUNT(*) AS n
        FROM demo_tbl
        WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        GROUP BY country, agegroup
        """
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        con.close()
        df_pre_pivot = pd.DataFrame(data, columns=['country_val', 'age_group_val', 'n'])
        df_pre_pivot['country_var'] = 'Country'
        df_pre_pivot['country'] = df_pre_pivot['country_val'].apply(lambda x: country_map[x])
        df_pre_pivot['row_filler_var_0'] = BLANK
        df_pre_pivot['row_filler_0'] = BLANK
        df_pre_pivot['age_group_var'] = 'Age Group'
        df_pre_pivot['age_group'] = df_pre_pivot['age_group_val'].apply(lambda x: age_group_map[x])
        df_pre_pivot['col_filler_var_0'] = BLANK
        df_pre_pivot['col_filler_0'] = BLANK
        df_pre_pivot['measure'] = 'Freq'
        df = (df_pre_pivot
            .pivot(
                index=['country_var', 'country', 'row_filler_var_0', 'row_filler_0'],
                columns=['age_group_var', 'age_group', 'col_filler_var_0', 'col_filler_0', 'measure'],
                values='n')
        )
        if debug: print(f"\nMIDDLE LEFT & RIGHT:\n{df}")
        return df

    ## MIDDLE MIDDLE
    @staticmethod
    def get_country_by_browser_and_age_group(*, debug=False) -> pd.DataFrame:
        con = sqlite.connect('sofa_db')
        cur = con.cursor()
        sql = """\
        SELECT country, browser, agegroup, COUNT(*) AS n
        FROM demo_tbl
        WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        GROUP BY country, browser, agegroup
        """
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        con.close()
        df_pre_pivot = pd.DataFrame(data, columns=['country_val', 'browser_val', 'age_group_val', 'n'])
        df_pre_pivot['country_var'] = 'Country'
        df_pre_pivot['country'] = df_pre_pivot['country_val'].apply(lambda x: country_map[x])
        df_pre_pivot['row_filler_var_0'] = BLANK
        df_pre_pivot['row_filler_0'] = BLANK
        df_pre_pivot['browser_var'] = 'Browser'
        df_pre_pivot['browser'] = df_pre_pivot['browser_val']
        df_pre_pivot['age_group_var'] = 'Age Group'
        df_pre_pivot['age_group'] = df_pre_pivot['age_group_val'].apply(lambda x: age_group_map[x])
        df_pre_pivot['measure'] = 'Freq'
        df = (df_pre_pivot
            .pivot(
                index=['country_var', 'country', 'row_filler_var_0', 'row_filler_0'],
                columns=['browser_var', 'browser', 'age_group_var', 'age_group', 'measure'],
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
        con = sqlite.connect('sofa_db')
        cur = con.cursor()
        sql = """\
        SELECT car, agegroup, COUNT(*) AS n
        FROM demo_tbl
        WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        AND car IN (2, 3)
        GROUP BY car, agegroup
        """
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        con.close()
        df_pre_pivot = pd.DataFrame(data, columns=['car_val', 'age_group_val', 'n'])
        df_pre_pivot['car_var'] = 'Car'
        df_pre_pivot['car'] = df_pre_pivot['car_val'].apply(lambda x: car_map[x])
        df_pre_pivot['row_filler_var_0'] = BLANK
        df_pre_pivot['row_filler_0'] = BLANK
        df_pre_pivot['age_group_var'] = 'Age Group'
        df_pre_pivot['age_group'] = df_pre_pivot['age_group_val'].apply(lambda x: age_group_map[x])
        df_pre_pivot['col_filler_var_0'] = BLANK
        df_pre_pivot['col_filler_0'] = BLANK
        df_pre_pivot['measure'] = 'Freq'
        df = (df_pre_pivot
            .pivot(
                index=['car_var', 'car', 'row_filler_var_0', 'row_filler_0'],
                columns=['age_group_var', 'age_group', 'col_filler_var_0', 'col_filler_0', 'measure'],
                values='n')
        )
        if debug: print(f"\nBOTTOM LEFT & RIGHT:\n{df}")
        return df

    ## BOTTOM MIDDLE
    @staticmethod
    def get_car_by_browser_and_age_group(*, debug=False) -> pd.DataFrame:
        con = sqlite.connect('sofa_db')
        cur = con.cursor()
        sql = """\
        SELECT car, browser, agegroup, COUNT(*) AS n
        FROM demo_tbl
        WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari')
        AND car IN (2, 3)
        GROUP BY car, browser, agegroup
        """
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        con.close()
        df_pre_pivot = pd.DataFrame(data, columns=['car_val', 'browser_val', 'age_group_val', 'n'])
        df_pre_pivot['car_var'] = 'Car'
        df_pre_pivot['car'] = df_pre_pivot['car_val'].apply(lambda x: car_map[x])
        df_pre_pivot['row_filler_var_0'] = BLANK
        df_pre_pivot['row_filler_0'] = BLANK
        df_pre_pivot['browser_var'] = 'Browser'
        df_pre_pivot['browser'] = df_pre_pivot['browser_val']
        df_pre_pivot['age_group_var'] = 'Age Group'
        df_pre_pivot['age_group'] = df_pre_pivot['age_group_val'].apply(lambda x: age_group_map[x])
        df_pre_pivot['measure'] = 'Freq'
        df = (df_pre_pivot
            .pivot(
                index=['car_var', 'car', 'row_filler_var_0', 'row_filler_0'],
                columns=['browser_var', 'browser', 'age_group_var', 'age_group', 'measure'],
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
    raw_col_tree = ['root', ['Age Group', ], ['Browser', ['Age Group', ]], ['Age Group Repeated', ]]  ## we will retain this order even if not sorted alphabetically as pandas will post-JOINing
    ## TOP
    df_top_left = GetData.get_country_gender_by_age_group(debug=debug)
    df_top_right = GetData.get_country_gender_by_browser_and_age_group(debug=debug)
    df_top = df_top_left.merge(df_top_right, how='outer', on=['country_var', 'country', 'gender_var', 'gender'])
    df_top_repeat = df_top_left.copy()
    df_top_repeat.rename(columns={'Age Group': 'Age Group Repeated'}, inplace=True)
    df_top = df_top.merge(df_top_repeat, how='outer', on=['country_var', 'country', 'gender_var', 'gender'])  ## join again to test ability to  handle col-spanning offsets etc
    ## MIDDLE
    df_middle_left = GetData.get_country_by_age_group(debug=debug)
    df_middle_right = GetData.get_country_by_browser_and_age_group(debug=debug)
    df_middle = df_middle_left.merge(df_middle_right, how='outer', on=['country_var', 'country', 'row_filler_var_0', 'row_filler_0'])
    df_middle_repeat = df_middle_left.copy()
    df_middle_repeat.rename(columns={'Age Group': 'Age Group Repeated'}, inplace=True)
    df_middle = df_middle.merge(df_middle_repeat, how='outer', on=['country_var', 'country', 'row_filler_var_0', 'row_filler_0'])
    ## BOTTOM
    df_bottom_left = GetData.get_car_by_age_group(debug=debug)
    df_bottom_right = GetData.get_car_by_browser_and_age_group(debug=debug)
    df_bottom = df_bottom_left.merge(df_bottom_right, how='outer', on=['car_var', 'car', 'row_filler_var_0', 'row_filler_0'])
    df_bottom_repeat = df_bottom_left.copy()
    df_bottom_repeat.rename(columns={'Age Group': 'Age Group Repeated'}, inplace=True)
    df_bottom = df_bottom.merge(df_bottom_repeat, how='outer', on=['car_var', 'car', 'row_filler_var_0', 'row_filler_0'])
    if debug:
        print(f"\nTOP:\n{df_top}\n\nMIDDLE:\n{df_middle}\n\nBOTTOM:\n{df_bottom}")
    ## COMBINE
    ## transpose, join, and re-transpose back. JOINing on rows works differently from columns and will include all items in sub-levels under the correct upper levels even if missing from the first multi-index
    ## e.g. if Age Group > 40-64 is missing from the first index it will not be appended on the end but will be alongside all its siblings so we end up with Age Group > >20, 20-29 30-39, 40-64, 65+
    ## Note - variable levels (odd numbered levels if 1 is the top level) should be in the same order as they were originally
    df_t = df_top.T.join(df_middle.T, how='outer')
    df_t = df_t.join(df_bottom.T, how='outer')
    df = df_t.T
    df.fillna(0, inplace=True)
    if debug: print(f"\nCOMBINED:\n{df}")
    df = columns_multi_index_fixer(df, raw_col_tree, debug=debug)
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

    # get_step_1_tbl_df(debug=True)
    main(debug=True, verbose=False)
