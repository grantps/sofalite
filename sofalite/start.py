"""
Will point at GUI later but good for running functions in the meanwhile.
"""
from webbrowser import open_new_tab

from sofalite.conf.data import ValDets
from sofalite.conf.paths import DATABASE_FPATH
from sofalite.output.css.default import get_style_dets
from sofalite.output.stats import anova as html_anova
from sofalite.sql_extraction.db import Sqlite
from sofalite.stats_calc import anova

DP = 3  ## will eventually get from GUI

with Sqlite(DATABASE_FPATH) as (_con, cur):
    grouping_fld_vals_dets = [ValDets(lbl='Male', val=1), ValDets(lbl='Female', val=2)]
    anova_results = anova.get_results(cur, tbl_name='demo_tbl',
        grouping_fld_lbl='Gender', grouping_fld_name='gender',
        grouping_fld_vals_dets=grouping_fld_vals_dets,
        grouping_val_is_numeric=True,
        measure_fld_lbl='Age', measure_fld_name='age', high_precision_required=False)
    style_dets = get_style_dets(rel_img_root='img')
    html = html_anova.make_anova_html(anova_results, style_dets, dp=DP, show_workings=False)
    fpath = '/home/g/demo.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")
