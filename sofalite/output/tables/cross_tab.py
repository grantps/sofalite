from functools import partial
from itertools import count
from typing import Literal, Sequence
from webbrowser import open_new_tab

from bs4 import BeautifulSoup
import pandas as pd
from pandas.io.formats.style import Styler
import numpy as np

from sofalite.conf.tables.misc import BLANK, PCT_MEASURES, Measure
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

def is_empty_th(th) -> bool:
    return th.string in (None, ' ', '\xa0')

def fix_top_left_box(raw_tbl_html: str, style_name: str, *, debug=False) -> str:
    """
    Merge top-left cells.

    https://www.crummy.com/software/BeautifulSoup/bs4/doc/

    https://www.crummy.com/software/BeautifulSoup/bs4/doc/#changing-tag-names-and-attributes

    E.g.
    <tr>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th colspan="2" halign="left">gender</th>
    <th colspan="6" halign="left">os</th>
    </tr>
    <tr>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th>male</th>
    <th>female</th>
    <th colspan="3" halign="left">ubuntu</th>
    <th colspan="3" halign="left">macos</th>
    </tr>
    <tr>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th>freq</th>
    <th>freq</th>
    <th>freq</th>
    <th>row %</th>
    <th>col %</th>
    <th>freq</th>
    <th>row %</th>
    <th>col %</th>
    </tr>
    Count total number of header rows.
    Count empty header cells in first table row i.e. <th></th>
    Replace first empty header cell with one that spans n cols and n rows
    Remove all (remaining) empty table cells
    """
    soup = BeautifulSoup(raw_tbl_html, 'html.parser')
    trs = soup.table.thead.find_all('tr')
    n_header_rows = len(trs)
    first_tr = trs[0]
    first_tr_ths = first_tr.find_all('th')
    first_tr_empty_ths = [th for th in first_tr_ths if is_empty_th(th)]
    n_empty = len(first_tr_empty_ths)
    if debug:
        print(f"{n_header_rows=}; {n_empty=}")
    tl_box_th = soup.new_tag('th')
    tl_box_th['colspan'] = str(n_empty)
    tl_box_th['rowspan'] = str(n_header_rows)
    tl_box_th['class'] = f"spaceholder-{style_name.replace('_', '-')}"
    first_tr_first_th = first_tr_ths[0]
    first_tr_first_th.replace_with(tl_box_th)
    ths = soup.table.thead.find_all('th')
    for th in ths[1:]:
        if is_empty_th(th):
            th.decompose()  ## bye bye!
    if debug:
        print(soup)
    tbl_html = str(soup)
    return tbl_html

def merge_col_blank_rows(raw_tbl_html: str, *, debug=False) -> str:
    """
    Male 	__blank__ 	__blank__ ==> Male colspan=3

    <th class="row_heading level1 row6" id="T_d3b21_level1_row6">Male</th>
    <th class="row_heading level2 row6" id="T_d3b21_level2_row6">__blank__</th>
    <th class="row_heading level3 row6" id="T_d3b21_level3_row6">__blank__</th>

    -->

    <th class="row_heading level1 row6" colspan=3 id="T_d3b21_level1_row6">Male</th>

    Get th's in order which have class = 'row_heading'
    Get positional idxs of non-__blank__ th's
    Pair idx and next_idx (None for the last one, and None for the first if only one)
    Gap = colspan. Set colspan if more than the default of 1.
    If next_idx is None, just use length of total list to work out any col-spanning.
    """
    soup = BeautifulSoup(raw_tbl_html, 'html.parser')
    ths = soup.table.find_all('th', class_='row_heading')
    df_ths = pd.DataFrame.from_dict({'th': ths})
    df_ths.reset_index(inplace=True)
    df_ths.rename(columns={'index': 'label_idx'}, inplace=True)
    max_idx = len(df_ths)  ## index of item after end
    df_labelled_ths = df_ths[df_ths.apply(lambda row: row['th'].string != BLANK, axis=1)].copy()
    ## remove all blanks now from actual soup
    for blank_th in df_ths[df_ths.apply(lambda row: row['th'].string == BLANK, axis=1)]['th']:
        blank_th.decompose()
    ## set up idxs ready for working out row spans
    next_labelled_ths = list(df_labelled_ths['label_idx'])[1:] + [max_idx]
    df_labelled_ths['next_label_idx'] = next_labelled_ths
    df_labelled_ths['span'] = df_labelled_ths['next_label_idx'] - df_labelled_ths['label_idx']
    if debug:
        print(df_labelled_ths)
    ## Add rowspan to each th where > 1
    for _i, row in df_labelled_ths[df_labelled_ths['span'] > 1].iterrows():
        row['th']['colspan'] = str(row['span'])
    if debug:
        print(soup)
    tbl_html = str(soup)
    return tbl_html

def merge_row_blank_rows(raw_tbl_html: str, *, debug=False, verbose=True) -> str:
    """
    Start at second-to-last (penultimate) tr in thead.
    Working across, look for BLANK th's.
    For each encountered, move upward through rows in same idx position until encountering a non-BLANK i.e. a label
    Count hops, set rowspan.
    At end, .decompose() all BLANK th's in thead.

    To implement, start by creating dict of rows with 0 being the key for the bottom row, 1 for the one above it etc.
    Each row will be a dict with left-to-right idxs as keys and ths as values.
    Why? So it is easy to reference th's relative to the one we are looking at.

    <thead>
    <tr>
    <th class="spaceholder-prestige-screen" colspan="4" rowspan="5"></th>
    <th class="col_heading level0 col0" colspan="15" id="T_6ef30_level0_col0">Age Group</th>
    <th class="col_heading level0 col15" colspan="15" id="T_6ef30_level0_col15">Web Browser</th>
    </tr>
    <tr>
    <th class="col_heading level1 col0" colspan="3" id="T_6ef30_level1_col0">&lt; 20</th>
    <th class="col_heading level1 col3" colspan="3" id="T_6ef30_level1_col3">20-29</th>
    <th class="col_heading level1 col6" colspan="3" id="T_6ef30_level1_col6">30-39</th>
    <th class="col_heading level1 col9" colspan="3" id="T_6ef30_level1_col9">40-64</th>
    <th class="col_heading level1 col12" colspan="3" id="T_6ef30_level1_col12">65+</th>
    <th class="col_heading level1 col15" colspan="3" id="T_6ef30_level1_col15">Google Chrome</th>
    <th class="col_heading level1 col18" colspan="3" id="T_6ef30_level1_col18">Firefox</th>
    <th class="col_heading level1 col21" colspan="3" id="T_6ef30_level1_col21">Internet Explorer</th>
    <th class="col_heading level1 col24" colspan="3" id="T_6ef30_level1_col24">Opera</th>
    <th class="col_heading level1 col27" colspan="3" id="T_6ef30_level1_col27">Safari</th>
    </tr>
    <tr>
    <th class="col_heading level2 col0" colspan="3" id="T_6ef30_level2_col0">__blank__</th>  <== first 5 are BLANK
    <th class="col_heading level2 col3" colspan="3" id="T_6ef30_level2_col3">__blank__</th>
    <th class="col_heading level2 col6" colspan="3" id="T_6ef30_level2_col6">__blank__</th>
    <th class="col_heading level2 col9" colspan="3" id="T_6ef30_level2_col9">__blank__</th>
    <th class="col_heading level2 col12" colspan="3" id="T_6ef30_level2_col12">__blank__</th>
    <th class="col_heading level2 col15" colspan="3" id="T_6ef30_level2_col15">Car</th>
    <th class="col_heading level2 col18" colspan="3" id="T_6ef30_level2_col18">Car</th>
    <th class="col_heading level2 col21" colspan="3" id="T_6ef30_level2_col21">Car</th>
    <th class="col_heading level2 col24" colspan="3" id="T_6ef30_level2_col24">Car</th>
    <th class="col_heading level2 col27" colspan="3" id="T_6ef30_level2_col27">Car</th>
    </tr>
    <tr>
    <th class="col_heading level3 col0" colspan="3" id="T_6ef30_level3_col0">__blank__</th> <== first 5 are BLANK
    <th class="col_heading level3 col3" colspan="3" id="T_6ef30_level3_col3">__blank__</th>
    <th class="col_heading level3 col6" colspan="3" id="T_6ef30_level3_col6">__blank__</th>
    <th class="col_heading level3 col9" colspan="3" id="T_6ef30_level3_col9">__blank__</th>
    <th class="col_heading level3 col12" colspan="3" id="T_6ef30_level3_col12">__blank__</th>
    <th class="col_heading level3 col15" id="T_6ef30_level3_col15">BMW</th>
    <th class="col_heading level3 col16" id="T_6ef30_level3_col16">Porsche</th>
    <th class="col_heading level3 col17" id="T_6ef30_level3_col17">Audi</th>
    <th class="col_heading level3 col18" id="T_6ef30_level3_col18">BMW</th>
    <th class="col_heading level3 col19" id="T_6ef30_level3_col19">Porsche</th>
    <th class="col_heading level3 col20" id="T_6ef30_level3_col20">Audi</th>
    <th class="col_heading level3 col21" id="T_6ef30_level3_col21">BMW</th>
    <th class="col_heading level3 col22" id="T_6ef30_level3_col22">Porsche</th>
    <th class="col_heading level3 col23" id="T_6ef30_level3_col23">Audi</th>
    <th class="col_heading level3 col24" id="T_6ef30_level3_col24">BMW</th>
    <th class="col_heading level3 col25" id="T_6ef30_level3_col25">Porsche</th>
    <th class="col_heading level3 col26" id="T_6ef30_level3_col26">Audi</th>
    <th class="col_heading level3 col27" id="T_6ef30_level3_col27">BMW</th>
    <th class="col_heading level3 col28" id="T_6ef30_level3_col28">Porsche</th>
    <th class="col_heading level3 col29" id="T_6ef30_level3_col29">Audi</th>
    </tr>
    <tr>
    <th class="col_heading level4 col0" id="T_6ef30_level4_col0">Freq</th> <== none are BLANK
    <th class="col_heading level4 col1" id="T_6ef30_level4_col1">Col %</th>
    <th class="col_heading level4 col2" id="T_6ef30_level4_col2">Row %</th>
    <th class="col_heading level4 col3" id="T_6ef30_level4_col3">Freq</th>
    <th class="col_heading level4 col4" id="T_6ef30_level4_col4">Col %</th>
    <th class="col_heading level4 col5" id="T_6ef30_level4_col5">Row %</th>
    <th class="col_heading level4 col6" id="T_6ef30_level4_col6">Freq</th>
    <th class="col_heading level4 col7" id="T_6ef30_level4_col7">Col %</th>
    <th class="col_heading level4 col8" id="T_6ef30_level4_col8">Row %</th>
    <th class="col_heading level4 col9" id="T_6ef30_level4_col9">Freq</th>
    <th class="col_heading level4 col10" id="T_6ef30_level4_col10">Col %</th>
    <th class="col_heading level4 col11" id="T_6ef30_level4_col11">Row %</th>
    <th class="col_heading level4 col12" id="T_6ef30_level4_col12">Freq</th>
    <th class="col_heading level4 col13" id="T_6ef30_level4_col13">Col %</th>
    <th class="col_heading level4 col14" id="T_6ef30_level4_col14">Row %</th>
    <th class="col_heading level4 col15" id="T_6ef30_level4_col15">Freq</th>
    <th class="col_heading level4 col16" id="T_6ef30_level4_col16">Freq</th>
    <th class="col_heading level4 col17" id="T_6ef30_level4_col17">Freq</th>
    <th class="col_heading level4 col18" id="T_6ef30_level4_col18">Freq</th>
    <th class="col_heading level4 col19" id="T_6ef30_level4_col19">Freq</th>
    <th class="col_heading level4 col20" id="T_6ef30_level4_col20">Freq</th>
    <th class="col_heading level4 col21" id="T_6ef30_level4_col21">Freq</th>
    <th class="col_heading level4 col22" id="T_6ef30_level4_col22">Freq</th>
    <th class="col_heading level4 col23" id="T_6ef30_level4_col23">Freq</th>
    <th class="col_heading level4 col24" id="T_6ef30_level4_col24">Freq</th>
    <th class="col_heading level4 col25" id="T_6ef30_level4_col25">Freq</th>
    <th class="col_heading level4 col26" id="T_6ef30_level4_col26">Freq</th>
    <th class="col_heading level4 col27" id="T_6ef30_level4_col27">Freq</th>
    <th class="col_heading level4 col28" id="T_6ef30_level4_col28">Freq</th>
    <th class="col_heading level4 col29" id="T_6ef30_level4_col29">Freq</th>
    </tr>
    </thead>
    """
    soup = BeautifulSoup(raw_tbl_html, 'html.parser')
    trs = soup.table.find('thead').find_all('tr')
    trs = reversed(trs)
    blank_ths = []
    th_coords = {}
    for row_idx, row in enumerate(trs):
        ths = row.find_all('th')
        blank_row_ths = [th for th in ths if th.string == BLANK]
        blank_ths.extend(blank_row_ths)
        ths_dict = {col_idx: th for col_idx, th in enumerate(ths)}
        th_coords[row_idx] = ths_dict
    penultimate_row = th_coords[1]
    for col_idx, th in penultimate_row.items():
        if th.string == BLANK:
            ## iterate upwards
            for hop_n in count(1):
                aligned_th = th_coords[1 + hop_n][col_idx]
                if aligned_th.string == BLANK:
                    continue
                else:
                    span = hop_n + 1
                    aligned_th['rowspan'] = str(span)
                    if debug and verbose:
                        print(f"{hop_n} {aligned_th}")
                    break
    ## remove all blanks now from actual soup
    for blank_th in blank_ths:
        blank_th.decompose()
    if debug:
        print(soup)
    tbl_html = str(soup)
    return tbl_html

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
