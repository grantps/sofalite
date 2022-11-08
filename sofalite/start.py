"""
Will point at GUI later but good for running functions in the meanwhile.
"""
import logging
from webbrowser import open_new_tab

from sofalite.conf.data import ValDets
from sofalite.conf.paths import DATABASE_FPATH
from sofalite.results.sql_extraction.db import Sqlite
from sofalite.results.stats import anova
from sofalite.results.html import anova as html_anova

DP = 3  ## will eventually get from GUI

with Sqlite(DATABASE_FPATH) as (_con, cur):
    grouping_fld_vals_dets = [ValDets(lbl='Male', val=1), ValDets(lbl='Female', val=2)]
    anova_results = anova.get_results(cur, tbl_name='demo_tbl',
        grouping_fld_lbl='Gender', grouping_fld_name='gender',
        grouping_fld_vals_dets=grouping_fld_vals_dets,
        grouping_val_is_numeric=True,
        measure_fld_lbl='Age', measure_fld_name='age', high_precision_required=False)
    html = html_anova.make_anova_html(anova_results, dp=DP)
    logging.info(html)
    with open('/home/g/demo.html', 'w') as f:
        f.write(html)
    open_new_tab(url=f"file:///home/g/demo.html")
