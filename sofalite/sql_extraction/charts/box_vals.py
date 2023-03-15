from collections import defaultdict
from itertools import groupby  ## actually quite performant

from sofalite.conf.charts.data.vals import (
    BoxplotCategoryItemValsSpec, BoxplotCategoryValsSpecs, BoxplotSeriesCategoryValsSpecs,
    BoxplotSeriesItemCategoryValsSpecs)
from sofalite.conf.misc import BoxplotType, SortOrder
from sofalite.sql_extraction.db import ExtendedCursor

def by_category(cur: ExtendedCursor, tbl_name: str,
        category_fld_name: str, category_fld_lbl: str,
        fld_name: str, fld_lbl: str,
        tbl_filt_clause: str | None = None,
        category_vals2lbls: dict | None = None,
        category_sort_order: SortOrder = SortOrder.VALUE,
        boxplot_type: BoxplotType = BoxplotType.IQR_1_PT_5_OR_INSIDE) -> BoxplotCategoryValsSpecs:
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{category_fld_name}` AS
      category_val,
      `{fld_name}`
    FROM {tbl_name}
    WHERE `{category_fld_name}` IS NOT NULL
    AND `{fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    ORDER BY `{category_fld_name}`, `{fld_name}`
    """
    ## get data
    cur.exe(sql)
    sorted_data = cur.fetchall()
    ## build result
    category_vals_specs = []
    for category_val, raw_vals in groupby(sorted_data, lambda t: t[0]):
        vals = [measure_val for _cat_val, measure_val in raw_vals]
        category_vals_spec = BoxplotCategoryItemValsSpec(
            category_val=category_val, category_val_lbl=category_vals2lbls.get(category_val, str(category_val)),
            vals=vals,
        )
        category_vals_specs.append(category_vals_spec)
    result = BoxplotCategoryValsSpecs(
        chart_lbl=None,
        series_fld_lbl=None,
        category_fld_lbl=category_fld_lbl,
        fld_lbl=fld_lbl,
        category_vals_specs=category_vals_specs,
        category_sort_order=category_sort_order,
        boxplot_type=boxplot_type,
    )
    return result

def by_series_category(cur: ExtendedCursor, tbl_name: str,
        series_fld_name: str, series_fld_lbl: str,
        category_fld_name: str, category_fld_lbl: str,
        fld_name: str, fld_lbl: str,
        tbl_filt_clause: str | None = None,
        series_vals2lbls: dict | None = None,
        category_vals2lbls: dict | None = None,
        category_sort_order: SortOrder = SortOrder.VALUE,
        boxplot_type: BoxplotType = BoxplotType.IQR_1_PT_5_OR_INSIDE) -> BoxplotSeriesCategoryValsSpecs:
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{series_fld_name}` AS
      series_val,
        `{category_fld_name}` AS
      category_val,
      `{fld_name}`
    FROM {tbl_name}
    WHERE `{series_fld_name}` IS NOT NULL
    AND `{category_fld_name}` IS NOT NULL
    AND `{fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    ORDER BY `{series_fld_name}`, `{category_fld_name}`, `{fld_name}`
    """
    ## get data
    cur.exe(sql)
    sorted_data = cur.fetchall()
    ## build result
    series_category_vals_specs_dict = defaultdict(list)
    for (series_val, category_val), raw_vals in groupby(sorted_data, lambda t: t[:2]):
        ## Gather by series
        vals = [measure_val for _chart_val, _cat_val, measure_val in raw_vals]
        category_vals_spec = BoxplotCategoryItemValsSpec(
            category_val=category_val, category_val_lbl=category_vals2lbls.get(category_val, str(category_val)),
            vals=vals,
        )
        series_category_vals_specs_dict[series_val].append(category_vals_spec)
    ## make item for each series
    series_category_vals_specs = []
    for series_val, category_vals_specs in series_category_vals_specs_dict.items():
        series_category_vals_spec = BoxplotSeriesItemCategoryValsSpecs(
            series_val=series_val,
            series_val_lbl=series_vals2lbls.get(series_val, series_val),
            category_vals_specs=category_vals_specs,
        )
        series_category_vals_specs.append(series_category_vals_spec)
    result = BoxplotSeriesCategoryValsSpecs(
        series_fld_lbl=None,
        category_fld_lbl=category_fld_lbl,
        fld_lbl=fld_lbl,
        series_category_vals_specs=series_category_vals_specs,
        category_sort_order=category_sort_order,
        boxplot_type=boxplot_type,
    )
    return result
