from pathlib import Path
from webbrowser import open_new_tab

from sofalite.output.stats.anova import AnovaSpec
from sofalite.output.stats.ttest_indep import TTestIndepSpec

def run_anova():
    stats = AnovaSpec(
        style_name='default', #'prestige_screen',
        tbl_name='demo_tbl',
        grouping_fld_name='country',
        group_vals=[1, 2, 3],
        measure_fld_name='age',
        tbl_filt_clause=None,
        cur=None,
        high_precision_required=False,
        dp=3,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/anova_age_by_country_prestige_screen_from_item.html')
    html_item_spec.to_file(fpath, 'ANOVA')
    open_new_tab(url=f"file://{fpath}")

def run_ttest_indep():
    stats = TTestIndepSpec(
        style_name='default',
        tbl_name='demo_tbl',
        grouping_fld_name='gender',
        group_a_val=1,
        group_b_val=2,
        measure_fld_name='age',
        tbl_filt_clause=None,
        cur=None,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofalite/reports/ttest_indep_age_by_country_from_item.html')
    html_item_spec.to_file(fpath, 'Independent t-test')
    open_new_tab(url=f"file://{fpath}")

if __name__ == '__main__':
    pass
    run_anova()
    run_ttest_indep()
