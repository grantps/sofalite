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

def fix_top_left_box(raw_tbl_html: str, style_name: str, *, debug=False, verbose=False) -> str:
    """
    Merge top-left cells.

    We start with a grid in the top-left corner - it has some labels we don't need and even an extra row
    depending on how pandas chooses, to display itself, possibly in a quirky way.

                              measure    Freq ...
    country_var    country     <====== pandas creates an extra row, including col labels, if, and only if, the entire column is the same

    To merge the top-left corner we need several things:
    1) the two numbers for n_rows and n_cols to span
    2) how to identify the ths to delete
    3) whether there is a row to delete (remove this first before working out total rows to span, or deleting ths)

    https://www.crummy.com/software/BeautifulSoup/bs4/doc/

    https://www.crummy.com/software/BeautifulSoup/bs4/doc/#changing-tag-names-and-attributes

    Step 1 - look at the final tr and see if the last th is empty. If so, remove that tr.
    Step 2 - use n_header_rows and n_header_cols to do spanning
    Step 3 - remove all other ths in top-left corner (not all of which are empty)
    """
    soup = BeautifulSoup(raw_tbl_html, 'html.parser')
    trs = soup.table.thead.find_all('tr')
    n_header_rows = len(trs)
    ## Step 1 Remove extraneous row (if present)
    last_tr = trs[-1]
    last_tr_ths = last_tr.find_all('th')
    last_th_in_last_tr = last_tr_ths[-1]
    last_th_in_last_tr_is_empty = is_empty_th(last_th_in_last_tr)
    if last_th_in_last_tr_is_empty:
        last_tr.decompose()  ## bye bye! Step 1 happens
        n_header_rows -= 1
        trs = soup.table.thead.find_all('tr')
    ## Step 2 Make spanned / merged cell
    first_tr = trs[0]
    first_tr_ths = first_tr.find_all('th')
    n_header_cols = 0
    for first_tr_th in first_tr_ths:
        if is_empty_th(first_tr_th):
            n_header_cols += 1
        else:
            break
    if debug:
        print(f"{n_header_rows=}; {n_header_cols=}")
    tl_box_th = soup.new_tag('th')
    tl_box_th['rowspan'] = str(n_header_rows)
    tl_box_th['colspan'] = str(n_header_cols)
    tl_box_th['class'] = f"spaceholder-{style_name.replace('_', '-')}"
    first_tr_first_th = first_tr_ths[0]
    first_tr_first_th.replace_with(tl_box_th)  ## Step 2 happens
    ## Step 3 Remove redundant ths
    ## for each header row, remove the first n_header_cols ths (except for first one in which case keep the first - the new spanned / merged th)
    for i, tr in enumerate(trs):
        first_header_row = (i == 0)
        start_idx = 1 if first_header_row else 0
        ths_in_header_row = tr.find_all('th')
        ths2kill = ths_in_header_row[start_idx: n_header_cols]
        for th2kill in ths2kill:
            th2kill.decompose()  ## bye bye! Step 3 happens
    if debug and verbose:
        print(soup)
    tbl_html = str(soup)
    return tbl_html

def merge_cols_of_blanks(raw_tbl_html: str, *, debug=False) -> str:
    """
    Male 	__blank__ 	__blank__ ==> Male colspan=3

    We want to get from:

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

def _get_upwards_row_to_col_idxs(trs_row_above_measures_first) -> dict[int: {int: str}]:
    """
    For example, we want to get from the HTML on the left to the dict on the right:

                              Browser                                                       Age Group                            row_idx: {col_idx: th, ...}
                Chrome                          Firefox                   <20        20-29       30-39      40-64        65+        2: {0: th(Chrome), 5: th(Firefox), 10: th(<20), 11: th(20-29), ...}
               Age Group                       Age Group                __blank__   __blank__   __blank__   __blank__   __blank__   1: {0: th(Age Group), 5: th(Age Group), 10: th(__blank__), 11: th(__blank__), ...}
    <20   20-29  30-39  40-64  65+    <20  20-29  30-39  40-64  65+ 	__blank__   __blank__   __blank__   __blank__   __blank__   0: {0: th(<20), 1: th(20-29), 2: th(30-39), ... 5: th(<20), ... 10: th(__blank__), 11: th(__blank__), ...}
    Freq  Freq   Freq   Freq  Freq   Freq  Freq   Freq   Freq   Freq      Freq        Freq        Freq        Freq        Freq      Ignored
    """
    upwards_row_to_col_idxs = {}
    for row_idx, tr in enumerate(trs_row_above_measures_first):
        col_idx_to_th = {}
        ths = tr.find_all('th')
        spans_to_add = 0
        for raw_col_idx, th in enumerate(ths):
            col_idx = raw_col_idx + spans_to_add
            col_idx_to_th[col_idx] = th
            extra_spans = int(th['colspan']) - 1 if th.get('colspan') is not None else 0  ## if a col spans 3 cols we only need to increment subsequent col_idxs by 2  TODO: check the attribute exists if 1 span
            if extra_spans:
                spans_to_add += extra_spans
        upwards_row_to_col_idxs[row_idx] = col_idx_to_th
    return upwards_row_to_col_idxs

def _get_blank_ths(trs) -> list:
    """
    Get list of table header (th) elements that are blank. At the end these will all be removed.
    """
    blank_ths = []
    for tr in trs:
        ths = tr.find_all('th')
        blank_ths_in_tr = [th for th in ths if th.string == BLANK]
        blank_ths.extend(blank_ths_in_tr)
    return blank_ths

def merge_rows_of_blanks(raw_tbl_html: str, *, debug=False, verbose=True) -> str:
    """
      20-29
    __blank__
    __blank__

    becomes

      20-29 rowspan=3

    etc

    We want to get from:
                              Browser                                                       Age Group
                Chrome                          Firefox                   <20        20-29       30-39      40-64        65+
               Age Group                       Age Group                __blank__   __blank__   __blank__   __blank__   __blank__
    <20   20-29  30-39  40-64  65+    <20  20-29  30-39  40-64  65+ 	__blank__ 	__blank__ 	__blank__ 	__blank__ 	__blank__    <========= row_above_measures (row index 0 counting upwards from bottom)
    Freq  Freq   Freq   Freq  Freq   Freq  Freq   Freq   Freq   Freq      Freq        Freq        Freq        Freq        Freq       <========= measures row

    -->
                              Browser                                                       Age Group
                Chrome                          Firefox                   <20        20-29       30-39      40-64        65+
               Age Group                       Age Group                    |          |           |          |           |   <=== pipes represent row spanning
    <20   20-29  30-39  40-64  65+    <20  20-29  30-39  40-64  65+ 	    |          |           |          |           |
    Freq  Freq   Freq   Freq  Freq   Freq  Freq   Freq   Freq   Freq      Freq        Freq        Freq        Freq        Freq

    We do this working upwards from the row_above_measures.
    We make that row 0 and the rows above it are 1, 2, .... etc.
    The outer process is to work across row_above_measures looking for BLANK (__blank__) th's.
    For each of these we then want to work upwards through the same horizontal position
    until we stop finding BLANKs in the th's and find an actual value in the th i.e. a label.
    We then row-span that valued (non-BLANK) th so it covers all the BLANK th's in the rows below it
    (we have kept track of the hops upwards).
    Because of col-spanning to our left, staying in the same position as we move upwards
    is not a simple matter of using the same th index position as in row_above_measures in the rows of th's above.
    More details on how that can be achieved in next paragraph.
    At end, .decompose() all BLANK th's in thead.

    Make a dict with row idx 0 being row_above_measures, 1 being the row above, and so on.
    Make the value a mapping from col_idx to th element. Because of col-spanning, some th col_idxs will not exist.
    For example:

                              Browser                                                       Age Group                            row_idx: {col_idx: th, ...}
                Chrome                          Firefox                   <20        20-29       30-39      40-64        65+        2: {0: th(Chrome), 5: th(Firefox), 10: th(<20), 11: th(20-29), ...}
               Age Group                       Age Group                __blank__   __blank__   __blank__   __blank__   __blank__   1: {0: th(Age Group), 5: th(Age Group), 10: th(__blank__), 11: th(__blank__), ...}
    <20   20-29  30-39  40-64  65+    <20  20-29  30-39  40-64  65+ 	__blank__   __blank__   __blank__   __blank__   __blank__   0: {0: th(<20), 1: th(20-29), 2: th(30-39), ... 5: th(<20), ... 10: th(__blank__), 11: th(__blank__), ...}
    Freq  Freq   Freq   Freq  Freq   Freq  Freq   Freq   Freq   Freq      Freq        Freq        Freq        Freq        Freq      Ignored

    Using the example above, we work across row_above_measures until we eventually encounter a BLANK at col_idx 10.
    In row_idx 1, col_idx 10 is still BLANK so we have 1 hop so far.
    In row_idx 2, col_idx 10 is not BLANK so we have 2 hops total and we can set the rowspan for that label th
    to the number of hops (2 in this case).
    Then move onto next col in row_above_measures.
    """
    soup = BeautifulSoup(raw_tbl_html, 'html.parser')
    trs = soup.table.find('thead').find_all('tr')
    trs_row_above_measures_first = reversed(trs)
    upwards_row_to_col_idxs = _get_upwards_row_to_col_idxs(trs_row_above_measures_first)
    row_above_measures = upwards_row_to_col_idxs[1]
    ## move rightwards across row_above_measures
    for col_idx, th in row_above_measures.items():
        if th.string == BLANK:
            ## iterate upwards
            for hop_n in count(1):
                aligned_th = upwards_row_to_col_idxs[1 + hop_n][col_idx]
                if aligned_th.string == BLANK:
                    continue
                else:
                    span = hop_n + 1
                    aligned_th['rowspan'] = str(span)
                    if debug and verbose:
                        print(f"{hop_n} {aligned_th}")
                    break
    blank_ths = _get_blank_ths(trs)
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
