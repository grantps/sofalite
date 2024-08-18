"""
Target Table
============
TODO: __blank__ in multi-indexes - don't flatten out / reset indexes

                                                                      browser > age_group                                           age_group

                        var_00       val_00     var_01     val_01 Chrome                         Firefox                         | <20        20-29      30-39      40-64      65+
                                                                     <20 20-29 30-39 40-64   65+     <20 20-29 30-39 40-64   65+ | __blank__  __blank__  __blank__  __blank__  __blank__
                    0  Country           NZ     Gender     Female    3.0   6.0   5.0  11.0  19.0    13.0  10.0   6.0  22.0  20.0 | 16         16         11         39         0.0
                    1  Country           NZ     Gender       Male    7.0  13.0  12.0  17.0  25.0    12.0  16.0   8.0  16.0  28.0 | 19         29         20         53         0.0
country > gender    2  Country  South Korea     Gender     Female   14.0   7.0   5.0  12.0  10.0    27.0  16.0   8.0  18.0  21.0 | 41         23         13         31         0.0
                    3  Country  South Korea     Gender       Male   18.0  10.0  11.0  23.0  11.0    22.0   7.0   9.0  25.0  28.0 | 40         17         20         39         0.0
                    4  Country        U.S.A     Gender     Female    7.0   4.0   5.0  16.0  15.0    18.0  14.0   8.0  28.0  31.0 | 25         18         13         46         0.0
                    5  Country        U.S.A     Gender       Male    0.0   0.0   0.0   0.0   0.0     0.0   0.0   0.0   0.0   0.0 | 28         15         21         39         0.0
                    _____________________________________________________________________________________________________________|_____________________________________________________
                    0  Country           NZ  __blank__  __blank__   10.0  19.0  17.0  28.0  44.0    25.0  26.0  14.0  38.0  48.0 | 35         45         31         92         66.0
country             1  Country  South Korea  __blank__  __blank__   32.0  17.0  16.0  35.0  21.0    49.0  23.0  17.0  43.0  49.0 | 81         40         33         70         78.0
                    2  Country        U.S.A  __blank__  __blank__   18.0   8.0  10.0  27.0  30.0    35.0  25.0  24.0  51.0  55.0 | 53         33         34         85         78.0


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

* OLD STEP 1 *********************************************************************************************************************************************

                      Chrome                         Firefox                               <20     20-29     30-39       65+   <20 20-29 30-39 40-64   65+
                         <20 20-29 30-39 40-64   65+     <20 20-29 30-39 40-64   65+ __blank__ __blank__ __blank__ __blank__
country
NZ          Female       3.0   6.0   5.0  11.0  19.0    13.0  10.0   6.0  22.0  20.0      16.0      16.0      11.0      39.0   0.0   0.0   0.0   0.0   0.0
            Male         7.0  13.0  12.0  17.0  25.0    12.0  16.0   8.0  16.0  28.0      19.0      29.0      20.0      53.0   0.0   0.0   0.0   0.0   0.0
South Korea Female      14.0   7.0   5.0  12.0  10.0    27.0  16.0   8.0  18.0  21.0      41.0      23.0      13.0      31.0   0.0   0.0   0.0   0.0   0.0
            Male        18.0  10.0  11.0  23.0  11.0    22.0   7.0   9.0  25.0  28.0      40.0      17.0      20.0      39.0   0.0   0.0   0.0   0.0   0.0
U.S.A       Female       7.0   4.0   5.0  16.0  15.0    18.0  14.0   8.0  28.0  31.0      25.0      18.0      13.0      46.0   0.0   0.0   0.0   0.0   0.0
            Male         0.0   0.0   0.0   0.0   0.0     0.0   0.0   0.0   0.0   0.0      28.0      15.0      21.0      39.0   0.0   0.0   0.0   0.0   0.0
NZ                       0.0   0.0   0.0   0.0   0.0     0.0   0.0   0.0   0.0   0.0       0.0       0.0       0.0       0.0  35.0  45.0  31.0  66.0  92.0
            __blank__   10.0  19.0  17.0  28.0  44.0    25.0  26.0  14.0  38.0  48.0       0.0       0.0       0.0       0.0   0.0   0.0   0.0   0.0   0.0
South Korea              0.0   0.0   0.0   0.0   0.0     0.0   0.0   0.0   0.0   0.0       0.0       0.0       0.0       0.0  81.0  40.0  33.0  78.0  70.0
            __blank__   32.0  17.0  16.0  35.0  21.0    49.0  23.0  17.0  43.0  49.0       0.0       0.0       0.0       0.0   0.0   0.0   0.0   0.0   0.0
U.S.A                    0.0   0.0   0.0   0.0   0.0     0.0   0.0   0.0   0.0   0.0       0.0       0.0       0.0       0.0  53.0  33.0  34.0  78.0  85.0
            __blank__   18.0   8.0  10.0  27.0  30.0    35.0  25.0  24.0  51.0  55.0       0.0       0.0       0.0       0.0   0.0   0.0   0.0   0.0   0.0


* NEW STEP 1 ****************************************************************************************************************************************************

                                              Browser                                                           Age Group
                                               Chrome                           Firefox                               <20     20-29     30-39       65+     40-64
                                            Age Group                         Age Group                         __blank__ __blank__ __blank__ __blank__ __blank__
                                                  <20 20-29 30-39 40-64   65+       <20 20-29 30-39 40-64   65+ __blank__ __blank__ __blank__ __blank__ __blank__
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


* DEMO **********************************************************************************************************************************************************************************************************************************************

                                    Age Group                                                                                                ... Web Browser
                                         < 20                     20-29                     30-39                     40-64                  ...     Firefox                Internet Explorer                Opera               Safari
                                    __blank__                 __blank__                 __blank__                 __blank__                  ...         Car                              Car                  Car                  Car
                                    __blank__                 __blank__                 __blank__                 __blank__                  ...         BMW Porsche   Audi               BMW Porsche   Audi   BMW Porsche  Audi    BMW Porsche  Audi
                                         Freq   Col %   Row %      Freq   Col %   Row %      Freq   Col %   Row %      Freq   Col %   Row %  ...        Freq    Freq   Freq              Freq    Freq   Freq  Freq    Freq  Freq   Freq    Freq  Freq
Country Japan   Gender    Male           4.00  50.00%  11.80%      6.00  66.70%  17.60%      4.00  36.40%  11.80%     11.00  61.10%  32.40%  ...        7.00    0.00   2.00              1.00    1.00   6.00  1.00    0.00  1.00   1.00    0.00  2.00
                          Female         4.00  50.00%  12.90%      3.00  33.30%   9.70%      7.00  63.60%  22.60%      7.00  38.90%  22.60%  ...        4.00    3.00   3.00              3.00    2.00   1.00  1.00    2.00  1.00   1.00    1.00  0.00
        Italy   Gender    Male          10.00  66.70%  34.50%      2.00  33.30%   6.90%      3.00  37.50%  10.30%      8.00  47.10%  27.60%  ...        7.00    3.00   2.00              4.00    1.00   0.00  2.00    1.00  0.00   2.00    1.00  0.00
                          Female         5.00  33.33%  16.70%      4.00  66.70%  13.30%      5.00  62.50%  16.70%      9.00  52.90%  30.00%  ...        6.00    3.00   1.00              2.00    1.00   2.00  0.00    0.00  0.00   6.00    0.00  3.00
        Germany Gender    Male          15.00  39.50%  17.00%     12.00  46.20%  13.60%     16.00  64.00%  18.20%     24.00  50.00%  27.30%  ...       13.00    6.00  13.00              9.00    4.00   8.00  4.00    0.00  4.00   3.00    3.00  4.00
                          Female        23.00  60.50%  22.80%     14.00  53.80%  13.90%      9.00  36.00%   8.90%     24.00  50.00%  23.80%  ...       13.00    5.00  16.00              9.00    7.00   4.00  6.00    1.00  6.00   6.00    2.00  6.00
Gender  Male    __blank__ __blank__     29.00  47.50%  19.20%     20.00  48.80%  13.20%     23.00  52.30%  15.20%     43.00  51.80%  28.50%  ...       27.00    9.00  17.00             14.00    6.00  14.00  7.00    1.00  5.00   6.00    4.00  6.00
        Female  __blank__ __blank__     32.00  52.50%  19.80%     21.00  51.20%  13.00%     21.00  47.70%  13.00%     40.00  48.20%  24.70%  ...       23.00   11.00  20.00             14.00   10.00   7.00  7.00    3.00  7.00  13.00    3.00  9.00

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

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 500)

BLANK = '__blank__'

age_group_map = {1: '<20', 2: '20-29', 3: '30-39', 4: '40-64', 5: '65+'}
country_map = {1: 'NZ', 2: 'South Korea', 3: 'U.S.A'}
gender_map = {1: 'Male', 2: 'Female'}


class GetData:

    ## TOP df

    ## TOP LEFT
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
        df = (df_pre_pivot
            .pivot(
                index=['country_var', 'country', 'gender_var', 'gender'],
                columns=['browser_var', 'browser', 'age_group_var', 'age_group'],
                values='n')
        )
        if debug: print(f"\nTOP LEFT:\n{df}")
        return df

    ## TOP RIGHT
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
        df = (df_pre_pivot
            .pivot(
                index=['country_var', 'country', 'gender_var', 'gender'],
                columns=['age_group_var', 'age_group', 'col_filler_var_0', 'col_filler_0'],
                values='n')
        )
        if debug: print(f"\nTOP RIGHT:\n{df}")
        return df

    ## BOTTOM df

    """
    Note - must have same columns for left as for TOP left df and for the right as for TOP right df
    TODO: Need filler in index
    """

    ## BOTTOM LEFT
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
        df = (df_pre_pivot
            .pivot(
                index=['country_var', 'country', 'row_filler_var_0', 'row_filler_0'],
                columns=['browser_var', 'browser', 'age_group_var', 'age_group'],
                values='n')
        )
        if debug: print(f"\nBOTTOM LEFT:\n{df}")
        return df

    ## BOTTOM RIGHT
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
        df = (df_pre_pivot
            .pivot(
                index=['country_var', 'country', 'row_filler_var_0', 'row_filler_0'],
                columns=['age_group_var', 'age_group', 'col_filler_var_0', 'col_filler_0'],
                values='n')
        )
        if debug: print(f"\nBOTTOM RIGHT:\n{df}")
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
    ## TOP
    df_top_left = GetData.get_country_gender_by_browser_and_age_group(debug=debug)
    df_top_right = GetData.get_country_gender_by_age_group(debug=debug)
    df_top = df_top_left.merge(df_top_right, how='outer', on=['country_var', 'country', 'gender_var', 'gender'])
    ## BOTTOM
    df_bottom_left = GetData.get_country_by_browser_and_age_group(debug=debug)
    df_bottom_right = GetData.get_country_by_age_group(debug=debug)
    df_bottom = df_bottom_left.merge(df_bottom_right, how='outer', on=['country_var', 'country', 'row_filler_var_0', 'row_filler_0'])
    if debug:
        print(f"\nTOP:\n{df_top}\n\nBOTTOM:\n{df_bottom}")
    ## COMBINE
    df = pd.concat([df_top, df_bottom], axis=0)
    df.fillna(0, inplace=True)
    if debug: print(f"\nCOMBINED:\n{df}")
    return df

def main():
    df = get_step_1_tbl_df(debug=True)
    print(df)

get_step_1_tbl_df(debug=True)
