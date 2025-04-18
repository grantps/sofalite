from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sofalite.conf.charts.output.standard import BarChartingSpec
from sofalite.conf.paths import DATABASE_FPATH
from sofalite.conf.stats.interfaces import SortOrder
from sofalite.output.charts.common import get_html
from sofalite.output.styles.misc import get_style_spec
from sofalite.sql_extraction.charts import freq_specs
from sofalite.sql_extraction.db import Sqlite
from sofalite.utils.misc import yaml2varlabels

yaml_fpath = Path('/home/g/projects/sofalite/store/var_labels.yaml')

@dataclass(frozen=True)
class SimpleBarChartSpec:
    style_name: str
    category_fld_name: str
    tbl_name: str
    tbl_filt_clause: str | None = None
    cur: Any | None = None
    category_sort_order: SortOrder = SortOrder.VALUE
    legend_lbl: str | None = None,
    rotate_x_lbls: bool = False,
    show_borders: bool = False,
    show_n_records: bool = True,
    x_axis_font_size: int = 12,
    y_axis_title: str = 'Freq'

    def to_html(self) -> str:
        ## style
        style_spec = get_style_spec(style_name=self.style_name)
        ## lbls
        var_labels = yaml2varlabels(yaml_fpath, vars2include=[self.category_fld_name, ], debug=False)
        category_fld_lbl = var_labels.var2var_lbl.get(self.category_fld_name, self.category_fld_name.title())
        category_vals2lbls = var_labels.var2val2lbl.get(self.category_fld_name, {})
        ## data
        local_cur = not bool(self.cur)
        if local_cur:
            with Sqlite(DATABASE_FPATH) as (_con, cur):
                intermediate_charting_spec = freq_specs.get_by_category_charting_spec(
                    cur, tbl_name=self.tbl_name,
                    category_fld_name=self.category_fld_name, category_fld_lbl=category_fld_lbl,
                    category_vals2lbls=category_vals2lbls,
                    tbl_filt_clause=None, category_sort_order=SortOrder.VALUE)
        else:
            intermediate_charting_spec = freq_specs.get_by_category_charting_spec(
                self.cur, tbl_name=self.tbl_name,
                category_fld_name=self.category_fld_name, category_fld_lbl=category_fld_lbl,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=None, category_sort_order=SortOrder.VALUE)
        ## chart details
        category_specs = intermediate_charting_spec.to_sorted_category_specs()
        indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec()
        charting_spec = BarChartingSpec(
            category_specs=category_specs,
            indiv_chart_specs=[indiv_chart_spec, ],
            legend_lbl=self.legend_lbl,
            rotate_x_lbls=self.rotate_x_lbls,
            show_borders=self.show_borders,
            show_n_records=self.show_n_records,
            x_axis_font_size=self.x_axis_font_size,
            x_axis_title=intermediate_charting_spec.category_fld_lbl,
            y_axis_title=self.y_axis_title,
        )
        ## output
        html = get_html(charting_spec, style_spec)
        return html
