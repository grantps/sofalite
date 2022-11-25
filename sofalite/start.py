"""
Will point at GUI later but good for running functions in the meanwhile.
"""
from webbrowser import open_new_tab

from sofalite.conf.data import ValDets
from sofalite.conf.paths import DATABASE_FPATH
from sofalite.output.css.misc import get_style_dets
from sofalite.output.stats import anova as html_anova
from sofalite.sql_extraction.db import Sqlite
from sofalite.stats_calc import anova

with Sqlite(DATABASE_FPATH) as (_con, cur):
    grouping_fld_vals_dets = [
        ValDets(lbl='Japan', val=1), ValDets(lbl='Italy', val=2), ValDets(lbl='Germany', val=3)]
    anova_results = anova.get_results(cur, tbl_name='demo_tbl',
        grouping_fld_lbl='Country of Residence', grouping_fld_name='country',
        grouping_fld_vals_dets=grouping_fld_vals_dets,
        grouping_val_is_numeric=True,
        measure_fld_lbl='Age', measure_fld_name='age', high_precision_required=False)
    style_dets = get_style_dets(style='prestige_screen')
    html = html_anova.make_anova_html(anova_results, style_dets, dp=3, show_workings=False)
    fpath = '/home/g/anova_age_by_country_prestige_screen.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")
