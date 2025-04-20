"""
Will point at GUI later but good for running functions in the meanwhile.

TODO: get mappings from YAML
"""
from webbrowser import open_new_tab

from sofalite.conf import DATABASE_FPATH
from sofalite.data_extraction.db import Sqlite
from sofalite.data_extraction.interfaces import ValDets
from sofalite.data_extraction.stats import anova as anova_data_extraction, ttest_indep as ttest_indep_data_extraction
from sofalite.output.stats import anova as anova_output, ttest_indep as ttest_indep_output
from sofalite.output.styles.misc import get_style_spec

def run_anova():
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        grouping_fld_vals_dets = [
            ValDets(lbl='Japan', val=1), ValDets(lbl='Italy', val=2), ValDets(lbl='Germany', val=3)]
        results = anova_data_extraction.get_results(cur, tbl_name='demo_tbl',
            grouping_fld_lbl='Country of Residence', grouping_fld_name='country',
            grouping_fld_vals_dets=grouping_fld_vals_dets,
            grouping_val_is_numeric=True,
            measure_fld_lbl='Age', measure_fld_name='age', high_precision_required=False)
        style_spec = get_style_spec(style_name='prestige_screen')
        html = anova_output.make_anova_html(results, style_spec, dp=3, show_workings=False)
        fpath = '/home/g/Documents/sofalite/reports/anova_age_by_country_prestige_screen.html'
        with open(fpath, 'w') as f:
            f.write(html)
        open_new_tab(url=f"file://{fpath}")

def run_ttest_indep():
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        group_a_val_dets = ValDets(lbl='Male', val=1)
        group_b_val_dets = ValDets(lbl='Female', val=2)
        results = ttest_indep_data_extraction.get_results(cur, tbl_name='demo_tbl',
            grouping_fld_lbl='Gender', grouping_fld_name='gender',
            group_a_val_dets=group_a_val_dets, group_b_val_dets=group_b_val_dets,
            grouping_val_is_numeric=True,
            measure_fld_lbl='Age', measure_fld_name='age')
        style_spec = get_style_spec(style_name='default')
        html = ttest_indep_output.make_ttest_indep_html(results, style_spec, dp=3, show_workings=False)
        fpath = '/home/g/Documents/sofalite/reports/ttest_indep_age_by_country_default.html'
        with open(fpath, 'w') as f:
            f.write(html)
        open_new_tab(url=f"file://{fpath}")

if __name__ == '__main__':
    pass
    run_anova()
    run_ttest_indep()
