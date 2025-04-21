from pathlib import Path

from sofalite.conf.main import DATABASE_FPATH
from sofalite.data_extraction.db import Sqlite
from sofalite.output.styles.misc import get_style_spec
from sofalite.output.tables.cross_tab import get_html as get_cross_tab_html
from sofalite.output.tables.freq import get_html as get_freq_html
from sofalite.output.tables.interfaces import CrossTabTblSpec, DimSpec, FreqTblSpec, Metric, Sort
from sofalite.output.tables.utils.misc import display_tbl
from sofalite.conf.main import VAR_LABELS

def run_main_poc_cross_tab():
    row_spec_0 = DimSpec(var='country', has_total=True,
        child=DimSpec(var='gender', has_total=True, sort_order=Sort.LBL))
    row_spec_1 = DimSpec(var='home_country', has_total=True, sort_order=Sort.LBL)
    row_spec_2 = DimSpec(var='car')

    col_spec_0 = DimSpec(var='agegroup', has_total=True, is_col=True)
    col_spec_1 = DimSpec(var='browser', has_total=True, is_col=True, sort_order=Sort.LBL,
         child=DimSpec(var='agegroup', has_total=True, is_col=True,
              pct_metrics=[Metric.ROW_PCT, Metric.COL_PCT]))
    col_spec_2 = DimSpec(var='std_agegroup', has_total=True, is_col=True)

    tbl_spec = CrossTabTblSpec(
        src_tbl='demo_cross_tab',
        tbl_filter="WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari') AND car IN (2, 3, 11)",
        row_specs=[row_spec_0, row_spec_1, row_spec_2],
        col_specs=[col_spec_0, col_spec_1, col_spec_2],
        var_labels=VAR_LABELS,
    )

    with Sqlite(DATABASE_FPATH) as (_con, cur):
        style_name = 'two_degrees'  #'default', 'two_degrees', 'grey_spirals'
        style_spec = get_style_spec(style_name)
        tbl_html = get_cross_tab_html(cur, tbl_spec=tbl_spec, style_spec=style_spec)
        display_tbl(tbl_html, tbl_name='integrated_into_std_code', style_name=style_spec.name)

def run_repeat_level_two_row_var_cross_tab():
    """
    Repeated row level 2 was no issue BUT a bug in the col ordering
    """
    row_spec_0 = DimSpec(var='country', has_total=True,
        child=DimSpec(var='gender', has_total=True, sort_order=Sort.LBL))
    row_spec_1 = DimSpec(var='agegroup', has_total=True,
        child=DimSpec(var='gender', has_total=True, sort_order=Sort.LBL))

    col_spec_0 = DimSpec(var='browser', has_total=True, is_col=True,
        pct_metrics=[Metric.ROW_PCT, Metric.COL_PCT])

    tbl_spec = CrossTabTblSpec(
        src_tbl='demo_cross_tab',
        tbl_filter="WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari') AND car IN (2, 3, 11)",
        row_specs=[row_spec_0, row_spec_1, ],
        col_specs=[col_spec_0, ],
        var_labels=VAR_LABELS,
    )

    with Sqlite(DATABASE_FPATH) as (_con, cur):
        style_name = 'grey_spirals'  #'default', 'two_degrees', 'grey_spirals'
        style_spec = get_style_spec(style_name)
        tbl_html = get_cross_tab_html(cur, tbl_spec=tbl_spec, style_spec=style_spec)
        display_tbl(tbl_html, tbl_name='repeat_level_two_row_var', style_name=style_spec.name)

def run_simple_freq_tbl():
    row_spec_0 = DimSpec(var='country', has_total=True,
        child=DimSpec(var='gender', has_total=True, sort_order=Sort.LBL))
    row_spec_1 = DimSpec(var='agegroup', has_total=True)

    tbl_spec = FreqTblSpec(
        src_tbl='demo_cross_tab',
        tbl_filter="WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari') AND car IN (2, 3, 11)",
        row_specs=[row_spec_0, row_spec_1, ],
        var_labels=VAR_LABELS,
        inc_col_pct=True,
    )

    with Sqlite(DATABASE_FPATH) as (_con, cur):
        style_name = 'grey_spirals'  # 'default', 'two_degrees', 'grey_spirals'
        style_spec = get_style_spec(style_name)
        tbl_html = get_freq_html(cur, tbl_spec=tbl_spec, style_spec=style_spec)
        display_tbl(tbl_html, tbl_name='freq_table_no_col_pct', style_name=style_spec.name)


if __name__ == '__main__':
    pass
    run_main_poc_cross_tab()
    run_repeat_level_two_row_var_cross_tab()
    run_simple_freq_tbl()
