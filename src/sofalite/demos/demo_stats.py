from webbrowser import open_new_tab

from sofalite.output.stats.anova import AnovaSpec
from sofalite.output.stats.ttest_indep import TTestIndepSpec

def run_anova():
    chart = AnovaSpec(
        style_name='prestige_screen',
        tbl_name='demo_tbl',
        grouping_fld_name='country',
        group_vals=[1, 2, 3],
        measure_fld_name='age',
        tbl_filt_clause=None,
        cur=None,
        high_precision_required=False,
        dp=3,
    )
    html = chart.to_html()

    fpath = '/home/g/Documents/sofalite/reports/anova_age_by_country_prestige_screen.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_ttest_indep():
    chart = TTestIndepSpec(
        style_name='default',
        tbl_name='demo_tbl',
        grouping_fld_name='gender',
        group_a_val=1,
        group_b_val=2,
        measure_fld_name='age',
        tbl_filt_clause=None,
        cur=None,
    )
    html = chart.to_html()

    fpath = '/home/g/Documents/sofalite/reports/ttest_indep_age_by_country_default.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

if __name__ == '__main__':
    pass
    run_anova()
    run_ttest_indep()
