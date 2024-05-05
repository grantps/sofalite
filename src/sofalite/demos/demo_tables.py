"""
Will point at GUI later but good for running functions in the meanwhile.
"""
import pandas as pd

from sofalite.conf.tables.misc import BLANK, Measure
from sofalite.output.tables.cross_tab import (
    apply_index_styles, display_tbl, fix_top_left_box, get_tbl_df,
    merge_col_blank_rows, merge_row_blank_rows, set_table_styles)

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 500)

def cross_tab_from_data():
    """
    TODO: JSON -> row_idx_tuples, col_idx_tuples, and data via SQL
    """
    dp = 2
    debug = True
    verbose = True
    row_idx_tuples = [
        ('Country', 'Japan', 'Gender', 'Male'),
        ('Country', 'Japan', 'Gender', 'Female'),
        ('Country', 'Italy', 'Gender', 'Male'),
        ('Country', 'Italy', 'Gender', 'Female'),
        ('Country', 'Germany', 'Gender', 'Male'),
        ('Country', 'Germany', 'Gender', 'Female'),
        ('Gender', 'Male', BLANK, BLANK),
        ('Gender', 'Female', BLANK, BLANK),
    ]
    col_idx_tuples = [
        ('Age Group', '< 20', BLANK, BLANK, Measure.FREQ),
        ('Age Group', '< 20', BLANK, BLANK, Measure.COL_PCT),
        ('Age Group', '< 20', BLANK, BLANK, Measure.ROW_PCT),
        ('Age Group', '20-29', BLANK, BLANK, Measure.FREQ),
        ('Age Group', '20-29', BLANK, BLANK, Measure.COL_PCT),
        ('Age Group', '20-29', BLANK, BLANK, Measure.ROW_PCT),
        ('Age Group', '30-39', BLANK, BLANK, Measure.FREQ),
        ('Age Group', '30-39', BLANK, BLANK, Measure.COL_PCT),
        ('Age Group', '30-39', BLANK, BLANK, Measure.ROW_PCT),
        ('Age Group', '40-64', BLANK, BLANK, Measure.FREQ),
        ('Age Group', '40-64', BLANK, BLANK, Measure.COL_PCT),
        ('Age Group', '40-64', BLANK, BLANK, Measure.ROW_PCT),
        ('Age Group', '65+', BLANK, BLANK, Measure.FREQ),
        ('Age Group', '65+', BLANK, BLANK, Measure.COL_PCT),
        ('Age Group', '65+', BLANK, BLANK, Measure.ROW_PCT),
        ('Web Browser', 'Google Chrome', 'Car', 'BMW', Measure.FREQ),
        ('Web Browser', 'Google Chrome', 'Car', 'Porsche', Measure.FREQ),
        ('Web Browser', 'Google Chrome', 'Car', 'Audi', Measure.FREQ),
        ('Web Browser', 'Firefox', 'Car', 'BMW', Measure.FREQ),
        ('Web Browser', 'Firefox', 'Car', 'Porsche', Measure.FREQ),
        ('Web Browser', 'Firefox', 'Car', 'Audi', Measure.FREQ),
        ('Web Browser', 'Internet Explorer', 'Car', 'BMW', Measure.FREQ),
        ('Web Browser', 'Internet Explorer', 'Car', 'Porsche', Measure.FREQ),
        ('Web Browser', 'Internet Explorer', 'Car', 'Audi', Measure.FREQ),
        ('Web Browser', 'Opera', 'Car', 'BMW', Measure.FREQ),
        ('Web Browser', 'Opera', 'Car', 'Porsche', Measure.FREQ),
        ('Web Browser', 'Opera', 'Car', 'Audi', Measure.FREQ),
        ('Web Browser', 'Safari', 'Car', 'BMW', Measure.FREQ),
        ('Web Browser', 'Safari', 'Car', 'Porsche', Measure.FREQ),
        ('Web Browser', 'Safari', 'Car', 'Audi', Measure.FREQ),
    ]
    data = [
        (4, 50.0, 11.8, 6, 66.7, 17.6, 4, 36.4, 11.8, 11, 61.1, 32.4, 9, 47.4, 26.5, 3, 3, 6, 7, 0, 2, 1, 1, 6, 1, 0, 1, 1, 0, 2),
        (4, 50.0, 12.9, 3, 33.3, 9.7, 7, 63.6, 22.6, 7, 38.9, 22.6, 10, 52.6, 32.3, 3, 3, 3, 4, 3, 3, 3, 2, 1, 1, 2, 1, 1, 1, 0),
        (10, 66.7, 34.5, 2, 33.3, 6.9, 3, 37.5, 10.3, 8, 47.1, 27.6, 6, 46.2, 20.7, 1, 3, 2, 7, 3, 2, 4, 1, 0, 2, 1, 0, 2, 1, 0),
        (5, 33.3333333333333, 16.7, 4, 66.7, 13.3, 5, 62.5, 16.7, 9, 52.9, 30.0, 7, 53.8, 23.3, 3, 1, 2, 6, 3, 1, 2, 1, 2, 0, 0, 0, 6, 0, 3),
        (15, 39.5, 17.0, 12, 46.2, 13.6, 16, 64.0, 18.2, 24, 50.0, 27.3, 21, 40.4, 23.9, 7, 3, 7, 13, 6, 13, 9, 4, 8, 4, 0, 4, 3, 3, 4),
        (23, 60.5, 22.8, 14, 53.8, 13.9, 9, 36.0, 8.9, 24, 50.0, 23.8, 31, 59.6, 30.7, 7, 2, 11, 13, 5, 16, 9, 7, 4, 6, 1, 6, 6, 2, 6),
        (29, 47.5, 19.2, 20, 48.8, 13.2, 23, 52.3, 15.2, 43, 51.8, 28.5, 36, 42.9, 23.8, 11, 9, 15, 27, 9, 17, 14, 6, 14, 7, 1, 5, 6, 4, 6),
        (32, 52.5, 19.8, 21, 51.2, 13.0, 21, 47.7, 13.0, 40, 48.2, 24.7, 48, 57.1, 29.6, 13, 6, 16, 23, 11, 20, 14, 10, 7, 7, 3, 7, 13, 3, 9),
    ]
    df = get_tbl_df(row_idx_tuples, col_idx_tuples, data, dp=dp, debug=debug)
    if debug:
        print(df)
    style_name = 'prestige_screen'
    pd_styler = set_table_styles(df.style)
    pd_styler = apply_index_styles(df, style_name, pd_styler, axis='rows')
    pd_styler = apply_index_styles(df, style_name, pd_styler, axis='columns')
    raw_tbl_html = pd_styler.to_html()
    if debug:
        print(raw_tbl_html)
    tbl_html = fix_top_left_box(raw_tbl_html, style_name)
    tbl_html = merge_col_blank_rows(tbl_html, debug=debug)
    tbl_html = merge_row_blank_rows(tbl_html, debug=debug, verbose=verbose)
    if debug:
        print(pd_styler.uuid)
        print(tbl_html)
    display_tbl(tbl_html, 'high_complexity_live', style_name)

cross_tab_from_data()
