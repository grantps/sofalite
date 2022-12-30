from dataclasses import dataclass

import pandas as pd

from sofalite.conf.charting.data import (
    CategoryFreqSpecs, CategoryItemFreqSpec,
    ChartCategoryFreqSpec, ChartCategoryFreqSpecs,
    ChartSeriesCategoryFreqSpec, ChartSeriesCategoryFreqSpecs,
    SeriesCategoryFreqSpec, SeriesCategoryFreqSpecs)
from sofalite.conf.data import ValDets
from sofalite.conf.stats_calc import Sample
from sofalite.sql_extraction.db import ExtendedCursor

def get_sample(cur: ExtendedCursor,
        tbl_name: str,
        grouping_filt_fld_name: str, grouping_filt_val_dets: ValDets, grouping_filt_val_is_numeric: bool,
        measure_fld_name: str,
        tbl_filt_clause: str | None = None) -> Sample:
    """
    Get list of non-missing values in numeric measure field for a group defined by another field
    e.g. getting weights for males.
    Must return list of floats.
    SQLite sometimes returns strings even though REAL data type. Not known why.
    Used, for example, in the independent samples t-test.
    Note - various filters might apply e.g. we want a sample for male weight
    but only where age > 10
    -
    :param tbl_name: name of table containing the data
    :param tbl_filt_clause: clause ready to put after AND in a WHERE filter.
     E.g. WHERE ... AND age > 10
     Sometimes there is a global filter active in SOFA for a table e.g. age > 10,
     and we will need to apply that filter to ensure we are only getting the correct values
    :param grouping_filt_fld_name: the grouping variable
     e.g. if we are interested in getting a sample of values for females
     then our grouping variable might be gender or sex
    :param grouping_filt_val_dets: the val dets for the grouping variable (lbl and val)
     e.g. if we are interested in getting a sample of values for females
     then our value might be 2 or 'female'
    :param grouping_filt_val_is_numeric: so we know whether to quote it or not
    :param measure_fld_name: e.g. weight
    """
    ## prepare clauses
    and_tbl_filt_clause = f"AND {tbl_filt_clause}" if tbl_filt_clause else ''
    if grouping_filt_val_is_numeric:
        grouping_filt_clause = f"{grouping_filt_fld_name} = {grouping_filt_val_dets.val}"
    else:
        grouping_filt_clause = f"{grouping_filt_fld_name} = '{grouping_filt_val_dets.val}'"
    and_grouping_filt_clause = f"AND {grouping_filt_clause}"
    ## assemble SQL
    sql = f"""
    SELECT `{measure_fld_name}`
    FROM {tbl_name}
    WHERE `{measure_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    {and_grouping_filt_clause}
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    ## coerce into floats because SQLite sometimes returns strings even if REAL
    sample_vals = [float(x[0]) for x in data]
    if len(sample_vals) < 2:
        raise Exception(f"Too few {measure_fld_name} values in sample for analysis "
            f"when getting sample for {grouping_filt_clause}")
    sample = Sample(lbl=grouping_filt_val_dets.lbl, vals=sample_vals)
    return sample

## Frequency & Percent (not aggregating a measure field)

def get_freq_specs_by_category(cur: ExtendedCursor, tbl_name: str,
        category_fld_name: str, category_fld_lbl: str, category_vals2lbls: dict | None = None,
        tbl_filt_clause: str | None = None) -> CategoryFreqSpecs:
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND {tbl_filt_clause}" if tbl_filt_clause else ''
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
    result = CategoryFreqSpecs(
        category_fld_lbl=category_fld_lbl,
        category_freq_specs=category_freq_specs,
    )
    return result

def get_freq_specs_by_series_category(cur: ExtendedCursor, tbl_name: str,
        series_fld_name: str, series_fld_lbl: str,
        category_fld_name: str, category_fld_lbl: str,
        series_vals2lbls: dict | None,
        category_vals2lbls: dict | None,
        tbl_filt_clause: str | None = None) -> SeriesCategoryFreqSpecs:
    series_vals2lbls = {} if series_vals2lbls is None else series_vals2lbls
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND {tbl_filt_clause}" if tbl_filt_clause else ''
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
    result = SeriesCategoryFreqSpecs(
        series_fld_lbl=series_fld_lbl,
        category_fld_lbl=category_fld_lbl,
        series_category_freq_specs=series_category_freq_specs,
    )
    return result

def get_freq_specs_by_chart_category(cur: ExtendedCursor, tbl_name: str,
        chart_fld_name: str, chart_fld_lbl: str,
        category_fld_name: str, category_fld_lbl: str,
        chart_vals2lbls: dict | None,
        category_vals2lbls: dict | None,
        tbl_filt_clause: str | None = None) -> ChartCategoryFreqSpecs:
    chart_vals2lbls = {} if chart_vals2lbls is None else chart_vals2lbls
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND {tbl_filt_clause}" if tbl_filt_clause else ''
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
    result = ChartCategoryFreqSpecs(
        chart_fld_lbl=chart_fld_lbl,
        category_fld_lbl=category_fld_lbl,
        chart_category_freq_specs=chart_category_freq_specs,
    )
    return result

def get_freq_specs_by_chart_series_category(cur: ExtendedCursor, tbl_name: str,
        chart_fld_name: str, chart_fld_lbl: str,
        series_fld_name: str, series_fld_lbl: str,
        category_fld_name: str, category_fld_lbl: str,
        chart_vals2lbls: dict | None,
        series_vals2lbls: dict | None,
        category_vals2lbls: dict | None,
        tbl_filt_clause: str | None = None) -> ChartSeriesCategoryFreqSpecs:
    chart_vals2lbls = {} if chart_vals2lbls is None else chart_vals2lbls
    series_vals2lbls = {} if series_vals2lbls is None else series_vals2lbls
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND {tbl_filt_clause}" if tbl_filt_clause else ''
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
    result = ChartSeriesCategoryFreqSpecs(
        chart_fld_lbl=chart_fld_lbl,
        series_fld_lbl=series_fld_lbl,
        category_fld_lbl=category_fld_lbl,
        chart_series_category_freq_specs=chart_series_category_freq_specs,
    )
    return result

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
            spec = get_freq_specs_by_category(
                cur=cur, tbl_name=tbl_name,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
        else:  ## series and category
            spec = get_freq_specs_by_series_category(
                cur=cur, tbl_name=tbl_name,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
                series_vals2lbls=series_vals2lbls,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
    else:  ## chart
        if series_fld_name is None:  ## chart and category only (no series)
            spec = get_freq_specs_by_chart_category(
                cur=cur, tbl_name=tbl_name,
                chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                chart_vals2lbls=chart_vals2lbls,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
        else: ## chart, series, and category
            spec = get_freq_specs_by_chart_series_category(
                cur=cur, tbl_name=tbl_name,
                chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
                series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                chart_vals2lbls=chart_vals2lbls,
                series_vals2lbls=series_vals2lbls,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
    return spec

## Aggregating measure field

@dataclass(frozen=True)
class AggSpec:
    category_val: float | str
    category_lbl: str
    measure_fld_name: str
    sum: float
    mean: float

##

# def get_agg_specs_by_category(cur: ExtendedCursor, tbl_name: str,
#         category_fld_name: str, category_vals2lbls: dict | None = None,
#         tbl_filt_clause: str | None = None, extra_filt_clause: str | None = None) -> Sequence[FreqSpec]:
#     """
#     Flexible - can be category only, by series as well, and by chart - all depending on extra_filt_clause.
#     """
#     category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
#     ## prepare clauses
#     and_tbl_filt_clause = f"AND {tbl_filt_clause}" if tbl_filt_clause else ''
#     and_extra_filt_clause = f"AND {extra_filt_clause}" if extra_filt_clause else ''
#     ## assemble SQL
#     sql = f"""\
#     SELECT
#         `{category_fld_name}` AS
#       category_val,
#         COUNT(*) AS
#       freq,
#         (100.0 * COUNT(*)) / (SELECT COUNT(*) FROM `{tbl_name}`) AS
#       raw_category_pct
#     FROM {tbl_name}
#     WHERE `{category_fld_name}` IS NOT NULL
#     {and_tbl_filt_clause}
#     {and_extra_filt_clause}
#     GROUP BY `{category_fld_name}`
#     ORDER BY `{category_fld_name}`
#     """
#     ## get data
#     cur.exe(sql)
#     data = cur.fetchall()
#     results = []
#     for category_val, freq, category_pct in data:
#         result = FreqSpec(
#             category_val=category_val, category_val_lbl=category_vals2lbls.get(category_val, str(category_val)),
#             freq=freq, category_pct=category_pct)
#         results.append(result)
#     return results
