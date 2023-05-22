"""
These functions are not responsible for sort order of category values (by value, by label etc).
Nor are they responsible for having placeholders for empty items
e.g. one country series lacks a certain web browser value
It is the dataclasses returned by these functions that are responsible for empty values.
Empty values are handled in their methods responsible for translating into charts specs
e.g. to_indiv_chart_spec().

Sort order always includes by value and by label. Only single chart, single series charts
also sort by increasing and decreasing.
"""
import pandas as pd

from sofalite.conf.charts.intermediate.freq_specs import (
    CategoryFreqSpecs, CategoryItemFreqSpec,
    ChartCategoryFreqSpec, ChartCategoryFreqSpecs,
    ChartSeriesCategoryFreqSpec, ChartSeriesCategoryFreqSpecs,
    SeriesCategoryFreqSpec, SeriesCategoryFreqSpecs)
from sofalite.conf.misc import SortOrder
from sofalite.sql_extraction.db import ExtendedCursor

def get_by_category_charting_spec(cur: ExtendedCursor, tbl_name: str,
        category_fld_name: str, category_fld_lbl: str, category_vals2lbls: dict | None = None,
        tbl_filt_clause: str | None = None,
        category_sort_order: SortOrder = SortOrder.VALUE) -> CategoryFreqSpecs:
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{category_fld_name}` AS
      category_val,
        COUNT(*) AS
      freq,
        (100.0 * COUNT(*)) / (SELECT COUNT(*) FROM `{tbl_name}`) AS
      raw_category_pct
    FROM {tbl_name}
    WHERE `{category_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY `{category_fld_name}`
    ORDER BY `{category_fld_name}`
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    ## build result
    category_freq_specs = []
    for category_val, freq, category_pct in data:
        freq_spec = CategoryItemFreqSpec(
            category_val=category_val, category_val_lbl=category_vals2lbls.get(category_val, str(category_val)),
            freq=int(freq), category_pct=category_pct)
        category_freq_specs.append(freq_spec)
    data_spec = CategoryFreqSpecs(
        category_fld_lbl=category_fld_lbl,
        category_freq_specs=category_freq_specs,
        category_sort_order=category_sort_order,
    )
    return data_spec

def get_by_series_category_charting_spec(cur: ExtendedCursor, tbl_name: str,
        series_fld_name: str, series_fld_lbl: str,
        category_fld_name: str, category_fld_lbl: str,
        series_vals2lbls: dict | None,
        category_vals2lbls: dict | None,
        tbl_filt_clause: str | None = None,
        category_sort_order: SortOrder = SortOrder.VALUE) -> SeriesCategoryFreqSpecs:
    series_vals2lbls = {} if series_vals2lbls is None else series_vals2lbls
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
        COUNT(*) AS
      freq,
        ((100.0 * COUNT(*))
        / (
          SELECT COUNT(*)
          FROM `{tbl_name}`
          WHERE `{series_fld_name}` = src.{series_fld_name}
        )) AS
      raw_category_pct
    FROM {tbl_name} AS src
    WHERE `{series_fld_name}` IS NOT NULL
    AND `{category_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY `{series_fld_name}`, `{category_fld_name}`
    ORDER BY `{series_fld_name}`, `{category_fld_name}`
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    cols = ['series_val', 'category_val', 'freq', 'raw_category_pct']
    df = pd.DataFrame(data, columns=cols)
    series_category_freq_specs = []
    for series_val in df['series_val'].unique():
        category_item_freq_specs = []
        for _i, (category_val, freq, raw_category_pct) in df.loc[
            df['series_val'] == series_val,
            ['category_val', 'freq', 'raw_category_pct']
        ].iterrows():
            freq_spec = CategoryItemFreqSpec(
                category_val=category_val,
                category_val_lbl=category_vals2lbls.get(category_val, category_val),
                freq=int(freq),
                category_pct=raw_category_pct,
            )
            category_item_freq_specs.append(freq_spec)
        series_category_freq_spec = SeriesCategoryFreqSpec(
            series_val=series_val,
            series_val_lbl=series_vals2lbls.get(series_val, series_val),
            category_freq_specs=category_item_freq_specs,
        )
        series_category_freq_specs.append(series_category_freq_spec)
    data_spec = SeriesCategoryFreqSpecs(
        series_fld_lbl=series_fld_lbl,
        category_fld_lbl=category_fld_lbl,
        series_category_freq_specs=series_category_freq_specs,
        category_sort_order=category_sort_order,
    )
    return data_spec

def get_by_chart_category_charting_spec(cur: ExtendedCursor, tbl_name: str,
        chart_fld_name: str, chart_fld_lbl: str,
        category_fld_name: str, category_fld_lbl: str,
        chart_vals2lbls: dict | None,
        category_vals2lbls: dict | None,
        tbl_filt_clause: str | None = None,
        category_sort_order: SortOrder = SortOrder.VALUE) -> ChartCategoryFreqSpecs:
    chart_vals2lbls = {} if chart_vals2lbls is None else chart_vals2lbls
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{chart_fld_name}` AS
      chart_val,
        `{category_fld_name}` AS
      category_val,
        COUNT(*) AS
      freq,
        ((100.0 * COUNT(*))
        / (
          SELECT COUNT(*)
          FROM `{tbl_name}`
          WHERE `{chart_fld_name}` = src.{chart_fld_name}
        )) AS
      raw_category_pct
    FROM {tbl_name} AS src
    WHERE `{chart_fld_name}` IS NOT NULL
    AND `{category_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY `{chart_fld_name}`, `{category_fld_name}`
    ORDER BY `{chart_fld_name}`, `{category_fld_name}`
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    cols = ['chart_val', 'category_val', 'freq', 'raw_category_pct']
    df = pd.DataFrame(data, columns=cols)
    chart_category_freq_specs = []
    for chart_val in df['chart_val'].unique():
        freq_specs = []
        for _i, (category_val, freq, raw_category_pct) in df.loc[
                    df['chart_val'] == chart_val,
                    ['category_val', 'freq', 'raw_category_pct']
                ].iterrows():
            freq_spec = CategoryItemFreqSpec(
                category_val=category_val,
                category_val_lbl=category_vals2lbls.get(category_val, category_val),
                freq=int(freq),
                category_pct=raw_category_pct,
            )
            freq_specs.append(freq_spec)
        chart_category_freq_spec = ChartCategoryFreqSpec(
            chart_val=chart_val,
            chart_val_lbl=chart_vals2lbls.get(chart_val, chart_val),
            category_freq_specs=freq_specs,
        )
        chart_category_freq_specs.append(chart_category_freq_spec)
    charting_spec = ChartCategoryFreqSpecs(
        chart_fld_lbl=chart_fld_lbl,
        category_fld_lbl=category_fld_lbl,
        chart_category_freq_specs=chart_category_freq_specs,
        category_sort_order=category_sort_order,
    )
    return charting_spec

def get_by_chart_series_category_charting_spec(cur: ExtendedCursor, tbl_name: str,
         chart_fld_name: str, chart_fld_lbl: str,
         series_fld_name: str, series_fld_lbl: str,
         category_fld_name: str, category_fld_lbl: str,
         chart_vals2lbls: dict | None,
         series_vals2lbls: dict | None,
         category_vals2lbls: dict | None,
         tbl_filt_clause: str | None = None,
         category_sort_order: SortOrder = SortOrder.VALUE) -> ChartSeriesCategoryFreqSpecs:
    chart_vals2lbls = {} if chart_vals2lbls is None else chart_vals2lbls
    series_vals2lbls = {} if series_vals2lbls is None else series_vals2lbls
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{chart_fld_name}` AS
      chart_val,
        `{series_fld_name}` AS
      series_val,
        `{category_fld_name}` AS
      category_val,
        COUNT(*) AS
      freq,
        ((100.0 * COUNT(*))
        / (
          SELECT COUNT(*)
          FROM `{tbl_name}`
          WHERE `{chart_fld_name}` = src.{chart_fld_name}
          AND `{series_fld_name}` = src.{series_fld_name}
        )) AS
      raw_category_pct
    FROM {tbl_name} AS src
    WHERE `{chart_fld_name}` IS NOT NULL
    AND `{series_fld_name}` IS NOT NULL
    AND `{category_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY `{chart_fld_name}`, `{series_fld_name}`, `{category_fld_name}`
    ORDER BY `{chart_fld_name}`, `{series_fld_name}`, `{category_fld_name}`
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    cols = ['chart_val', 'series_val', 'category_val', 'freq', 'raw_category_pct']
    df = pd.DataFrame(data, columns=cols)
    chart_series_category_freq_specs = []
    for chart_val in df['chart_val'].unique():
        series_category_freq_specs = []
        for series_val in df.loc[df['chart_val'] == chart_val, 'series_val'].unique():
            freq_specs = []
            for _i, (category_val, freq, raw_category_pct) in df.loc[
                (df['chart_val'] == chart_val) & (df['series_val'] == series_val),
                ['category_val', 'freq', 'raw_category_pct']
            ].iterrows():
                freq_spec = CategoryItemFreqSpec(
                    category_val=category_val,
                    category_val_lbl=category_vals2lbls.get(category_val, category_val),
                    freq=int(freq),
                    category_pct=raw_category_pct,
                )
                freq_specs.append(freq_spec)
            series_category_freq_spec = SeriesCategoryFreqSpec(
                series_val=series_val,
                series_val_lbl=series_vals2lbls.get(series_val, series_val),
                category_freq_specs=freq_specs,
            )
            series_category_freq_specs.append(series_category_freq_spec)
        chart_series_category_freq_spec = ChartSeriesCategoryFreqSpec(
            chart_val=chart_val,
            chart_val_lbl=chart_vals2lbls.get(chart_val, str(chart_val)),
            series_category_freq_specs=series_category_freq_specs,
        )
        chart_series_category_freq_specs.append(chart_series_category_freq_spec)
    data_spec = ChartSeriesCategoryFreqSpecs(
        chart_fld_lbl=chart_fld_lbl,
        series_fld_lbl=series_fld_lbl,
        category_fld_lbl=category_fld_lbl,
        chart_series_category_freq_specs=chart_series_category_freq_specs,
        category_sort_order=category_sort_order,
    )
    return data_spec

def get_freq_specs(cur: ExtendedCursor, tbl_name: str,
        category_fld_name: str, category_fld_lbl: str,
        chart_fld_name: str | None = None, chart_fld_lbl: str | None = None,
        series_fld_name: str | None = None, series_fld_lbl: str | None = None,
        chart_vals2lbls: dict | None = None,
        series_vals2lbls: dict | None = None,
        category_vals2lbls: dict | None = None,
        tbl_filt_clause: str | None = None) -> ChartSeriesCategoryFreqSpecs:
    """
    Single interface irrespective of which settings are None
    e.g. if no By Chart variable selected can still use same interface.
    Convenient when calling code from a GUI.
    """
    if chart_fld_name is None:  ## no chart
        if series_fld_name is None:  ## no series (so category only)
            data_spec = get_by_category_charting_spec(
                cur=cur, tbl_name=tbl_name,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
        else:  ## series and category
            data_spec = get_by_series_category_charting_spec(
                cur=cur, tbl_name=tbl_name,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
                series_vals2lbls=series_vals2lbls,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
    else:  ## chart
        if series_fld_name is None:  ## chart and category only (no series)
            data_spec = get_by_chart_category_charting_spec(
                cur=cur, tbl_name=tbl_name,
                chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                chart_vals2lbls=chart_vals2lbls,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
        else:  ## chart, series, and category
            data_spec = get_by_chart_series_category_charting_spec(
                cur=cur, tbl_name=tbl_name,
                chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
                series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                chart_vals2lbls=chart_vals2lbls,
                series_vals2lbls=series_vals2lbls,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
    return data_spec
