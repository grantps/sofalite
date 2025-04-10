"""
Run entirely from config and library modules.
"""
from pathlib import Path
from webbrowser import open_new_tab

from sofalite.conf.paths import DATABASE_FPATH
from sofalite.conf.tables.output.cross_tab import DimSpec, TblSpec
from sofalite.conf.tables.misc import Metric, Sort
from sofalite.output.styles.misc import get_style_spec
from sofalite.output.tables.cross_tab import get_html
from sofalite.sql_extraction.db import Sqlite
from sofalite.utils.labels import yaml2varlabels

def main():
    store_root = Path(__file__).parent.parent.parent.parent.parent / 'store'
    yaml_fpath = store_root / 'var_labels.yaml'

    row_spec_0 = DimSpec(var='country', has_total=True,
        child=DimSpec(var='gender', has_total=True, sort_order=Sort.LBL))
    row_spec_1 = DimSpec(var='home_country', has_total=True, sort_order=Sort.LBL)
    row_spec_2 = DimSpec(var='car')

    col_spec_0 = DimSpec(var='agegroup', has_total=True, is_col=True)
    col_spec_1 = DimSpec(var='browser', has_total=True, is_col=True, sort_order=Sort.LBL,
         child=DimSpec(var='agegroup', has_total=True, is_col=True,
              pct_metrics=[Metric.ROW_PCT, Metric.COL_PCT]))
    col_spec_2 = DimSpec(var='std_agegroup', has_total=True, is_col=True)

    tbl_spec = TblSpec(
        tbl='demo_cross_tab',  ## made in step_5_format_numbers_poc
        tbl_filter="WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari') AND car IN (2, 3, 11)",
        row_specs=[row_spec_0, row_spec_1, row_spec_2],
        col_specs=[col_spec_0, col_spec_1, col_spec_2],
    )

    var_labels = yaml2varlabels(yaml_fpath,
        vars2include=['agegroup', 'browser', 'car', 'country', 'gender', 'home_country',
            'std_agegroup'], debug=False)

    style_spec = get_style_spec(style_name='prestige_screen')
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        tbl_html = get_html(cur, tbl_spec, var_labels, dp=3, style_spec=style_spec, debug=False, verbose=False)
    tbl_name = 'cross_tab_og'
    fpath = f"/home/g/Documents/sofalite/reports/{tbl_name}.html"
    with open(fpath, 'w') as f:
        f.write(tbl_html)
    open_new_tab(f"file://{fpath}")

if __name__ == '__main__':
    main()
