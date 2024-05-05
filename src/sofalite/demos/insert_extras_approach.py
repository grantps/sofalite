"""
Strategy - do the simplest thing first.

1) Ignore totals (especially nested totals!) and row / col percentages.
Just (just!) get the data for the table resulting from the intersection
of all the row and column ssub-trees.
2) Afterwards, add totals for rows, then totals for columns.
3) Then calculate row and column percentages.



*** 1) GET BASIC DATA ********************************************************************************************

Note - we flatten out the row multi-index. This falttening results in a column per row variable (at this
point we're ignoring the splitting of each row variable into variable name and value).
Given it is a column, it has to have as many levels as the column dimension columns.
So if there are two column dimension levels each row column will need to be a two-tuple e.g. ('gender', '').
If there were three column dimension levels the row column would need to be a three-tuple e.g. ('gender', '', '').
"""

import pandas as pd
import sqlite3 as sqlite

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 500)

BLANK = '__blank__'

agegroup_map = {1: '<20', 2: '20-29', 3: '30-39', 4: '40-64', 5: '65+'}
country_map = {1: 'NZ', 2: 'South Korea', 3: 'U.S.A'}
gender_map = {1: 'Male', 2: 'Female'}


## TOP df

## TOP LEFT
def get_country_gender_by_browser_and_agegroup(*, debug=False) -> pd.DataFrame:
    """
    Wipe out gender 1 from country 3 to confirm the combined table
    has gender 1 from country 3 anyway because it is in the agegroup
    table.

    Note - when multi-level, every column is a tuple e.g. a row dimension column (once index reset)
    might be ('country', '') and a column dimension column ('Firefox', '20-29').
    There will be empty string items padding out row dimension columns so that there will be as many
    tuple items as column dimension levels.
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
    df_raw = pd.DataFrame(data, columns=['country', 'gender', 'browser', 'agegroup', 'n'])
    df_raw['agegroup'] = df_raw['agegroup'].apply(lambda x: agegroup_map[x])
    df = (df_raw
        .pivot(index=['country', 'gender'], columns=['browser', 'agegroup'], values='n')
        .reset_index())
    cols = list(df.columns)
    df['var_00'] = 'Country'
    df['val_00'] = df[('country', '')].apply(lambda x: country_map[x])
    df['var_01'] = 'Gender'
    df['val_01'] = df[('gender', '')].apply(lambda x: gender_map[x])
    row_dim_cols = [('var_00', ''), ('val_00', ''), ('var_01', ''), ('val_01', '')]
    col_dim_cols = [col for col in cols if col not in [('country', ''), ('gender', '')]]
    cols2keep = row_dim_cols + col_dim_cols
    df = df[cols2keep]
    if debug: print(f"\nTOP LEFT:\n{df}")
    return df

## TOP RIGHT
def get_country_gender_by_agegroup(*, debug=False) -> pd.DataFrame:
    """
    Wipe out agegroup 4 to confirm the combined table
    has agegroup 4 column anyway because it is in the country row
    table.

    Needs two level column dimension columns because left df has two column dimension levels
    i.e. browser and agegroup. So dummy variable needed.
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
    df_raw = pd.DataFrame(data, columns=['country', 'gender', 'agegroup', 'n'])
    df_raw['agegroup'] = df_raw['agegroup'].apply(lambda x: agegroup_map[x])
    df_raw['dummy'] = ''
    df = (df_raw
        .pivot(index=['country', 'gender'], columns=['agegroup', 'dummy'], values='n')
        .reset_index())
    cols = list(df.columns)
    df['var_00'] = 'Country'
    df['val_00'] = df[('country', '')].apply(lambda x: country_map[x])
    df['var_01'] = 'Gender'
    df['val_01'] = df[('gender', '')].apply(lambda x: gender_map[x])
    row_dim_cols = [('var_00', ''), ('val_00', ''), ('var_01', ''), ('val_01', '')]
    col_dim_cols = [col for col in cols if col not in [('country', ''), ('gender', '')]]
    cols2keep = row_dim_cols + col_dim_cols
    df = df[cols2keep]
    if debug: print(f"\nTOP RIGHT:\n{df}")
    return df


## BOTTOM df

"""
Note - must have same columns for left as for TOP left df and for the right as for TOP right df
"""

## BOTTOM LEFT
def get_country_by_browser_and_agegroup(*, debug=False) -> pd.DataFrame:
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
    df_raw = pd.DataFrame(data, columns=['country', 'browser', 'agegroup', 'n'])
    df_raw['agegroup'] = df_raw['agegroup'].apply(lambda x: agegroup_map[x])
    df = (df_raw
        .pivot(index='country', columns=['browser', 'agegroup'], values='n')
        .reset_index())
    cols = list(df.columns)
    df['var_00'] = 'Country'
    df['val_00'] = df[('country', '')].apply(lambda x: country_map[x])
    df['var_01'] = BLANK
    df['val_01'] = BLANK
    row_dim_cols = [('var_00', ''), ('val_00', ''), ('var_01', ''), ('val_01', '')]
    col_dim_cols = [col for col in cols if col != ('country', '')]
    cols2keep = row_dim_cols + col_dim_cols
    df = df[cols2keep]
    if debug: print(f"\nBOTTOM LEFT:\n{df}")
    return df

## BOTTOM RIGHT
def get_country_by_agegroup(*, debug=False) -> pd.DataFrame:
    """
    Needs two level column dimension columns because left df has two column dimension levels
    i.e. browser and agegroup. So dummy variable needed.
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
    df_raw = pd.DataFrame(data, columns=['country', 'agegroup', 'n'])
    df_raw['agegroup'] = df_raw['agegroup'].apply(lambda x: agegroup_map[x])
    df_raw['dummy'] = ''
    df = (df_raw
        .pivot(index='country', columns=['agegroup', 'dummy'], values='n')
        .reset_index())
    cols = list(df.columns)
    df['var_00'] = 'Country'
    df['val_00'] = df['country'].apply(lambda x: country_map[x])
    df['var_01'] = BLANK
    df['val_01'] = BLANK
    row_dim_cols = [('var_00', ''), ('val_00', ''), ('var_01', ''), ('val_01', '')]
    col_dim_cols = [col for col in cols if col != ('country', '')]
    cols2keep = row_dim_cols + col_dim_cols
    df = df[cols2keep]
    if debug: print(f"\nBOTTOM RIGHT:\n{df}")
    return df


## COMBINED - TOP + BOTTOM

def get_freqs_df(*, debug=False) -> pd.DataFrame:
    """
    Note - using pd.concat or df.merge(how='outer') has the same result but I use merge for horizontal joining
    to avoid repeating the row dimension columns e.g. country and gender.
    """
    row_dim_cols = [('var_00', ''), ('val_00', ''), ('var_01', ''), ('val_01', '')]
    ## TOP
    df_top_left = get_country_gender_by_browser_and_agegroup(debug=debug)
    df_top_right = get_country_gender_by_agegroup(debug=debug)
    df_top = df_top_left.merge(df_top_right, how='outer', on=row_dim_cols)
##    df_top.sort_values(by=row_dim_cols, inplace=True)
    ## BOTTOM
    df_bottom_left = get_country_by_browser_and_agegroup(debug=debug)
    df_bottom_right = get_country_by_agegroup(debug=debug)
    df_bottom = df_bottom_left.merge(df_bottom_right, how='outer', on=row_dim_cols)
##    df_top.sort_values(by=row_dim_cols, inplace=True)
    if debug:
        print(f"\nTOP:\n{df_top}\n\nBOTTOM:\n{df_bottom}")
    ## COMBINE
    df = pd.concat([df_top, df_bottom], axis=0)
    df.fillna(0, inplace=True)
    if debug: print(f"\nCOMBINED:\n{df}")
    return df


df = get_freqs_df(debug=False)
print(df)

