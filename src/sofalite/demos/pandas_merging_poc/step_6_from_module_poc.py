"""
Run entirely from config and library modules.
"""
from pathlib import Path

from sofalite.conf.tables.output.cross_tab import DimSpec, TblSpec
from sofalite.conf.tables.misc import Metric, Sort
from sofalite.output.tables.cross_tab import display_cross_tab
from sofalite.utils.labels import yaml2varlabels

def main():
    store_root = Path(__file__).parent.parent.parent.parent.parent / 'store'
    db_fpath = store_root / 'sofa_db'
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

    display_cross_tab(db_fpath, tbl_spec, var_labels, 'cross_tab_og', dp=3, debug=False, verbose=False)

if __name__ == '__main__':
    main()
