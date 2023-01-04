import pandas as pd

from sofalite.conf.charts.data.xys import (ChartSeriesXYSpec, ChartSeriesXYSpecs, ChartXYSpec, ChartXYSpecs,
    SeriesXYSpec, SeriesXYSpecs, XYSpecs)
from sofalite.sql_extraction.db import ExtendedCursor

def by_xy(cur: ExtendedCursor, tbl_name: str,
        x_fld_name: str, y_fld_name: str,
        tbl_filt_clause: str | None = None) -> XYSpecs:
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{x_fld_name}` AS x,
        `{y_fld_name}` AS y
    FROM {tbl_name}
    WHERE `{x_fld_name}` IS NOT NULL
    AND `{y_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    ## build result
    result = XYSpecs(
        xys=data,
    )
    return result

def by_series_xy(cur: ExtendedCursor, tbl_name: str,
        series_fld_name: str,
        x_fld_name: str, y_fld_name: str,
        series_vals2lbls: dict | None,
        tbl_filt_clause: str | None = None) -> SeriesXYSpecs:
    ## prepare clauses
    series_vals2lbls = {} if series_vals2lbls is None else series_vals2lbls
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{series_fld_name}` AS series_val,
        `{x_fld_name}` AS x,
        `{y_fld_name}` AS y
    FROM {tbl_name}
    WHERE `{x_fld_name}` IS NOT NULL
    AND `{y_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    cols = ['series_val', 'x', 'y']
    df = pd.DataFrame(data, columns=cols)
    ## build result
    series_xy_specs = []
    for series_val in df['series_val'].unique():
        xys = df.loc[df['series_val'] == series_val, ['x', 'y']].to_records(index=False).tolist()
        series_xy_spec = SeriesXYSpec(
            lbl=series_vals2lbls.get(series_val, series_val),
            xys=xys,
        )
        series_xy_specs.append(series_xy_spec)
    result = SeriesXYSpecs(
        series_xy_specs=series_xy_specs,
    )
    return result

def by_chart_xy(cur: ExtendedCursor, tbl_name: str,
        chart_fld_name: str, chart_fld_lbl: str,
        x_fld_name: str, y_fld_name: str,
        chart_vals2lbls: dict | None,
        tbl_filt_clause: str | None = None) -> ChartXYSpecs:
    ## prepare clauses
    chart_vals2lbls = {} if chart_vals2lbls is None else chart_vals2lbls
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{chart_fld_name}` AS charts_val,
        `{x_fld_name}` AS x,
        `{y_fld_name}` AS y
    FROM {tbl_name}
    WHERE `{x_fld_name}` IS NOT NULL
    AND `{y_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    cols = ['charts_val', 'x', 'y']
    df = pd.DataFrame(data, columns=cols)
    ## build result
    charts_xy_specs = []
    for chart_val in df['charts_val'].unique():
        xys = df.loc[df['charts_val'] == chart_val, ['x', 'y']].to_records(index=False).tolist()
        chart_xy_spec = ChartXYSpec(
            lbl=f"{chart_fld_lbl}: {chart_vals2lbls.get(chart_val, chart_val)}",
            xys=xys,
        )
        charts_xy_specs.append(chart_xy_spec)
    result = ChartXYSpecs(
        charts_xy_specs=charts_xy_specs,
    )
    return result

def by_chart_series_xy(cur: ExtendedCursor, tbl_name: str,
        chart_fld_name: str, chart_fld_lbl: str,
        series_fld_name: str,
        x_fld_name: str, y_fld_name: str,
        chart_vals2lbls: dict | None,
        series_vals2lbls: dict | None,
        tbl_filt_clause: str | None = None) -> ChartSeriesXYSpecs:
    ## prepare clauses
    chart_vals2lbls = {} if chart_vals2lbls is None else chart_vals2lbls
    series_vals2lbls = {} if series_vals2lbls is None else series_vals2lbls
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{chart_fld_name}` AS chart_val,
        `{series_fld_name}` AS series_val,
        `{x_fld_name}` AS x,
        `{y_fld_name}` AS y
    FROM {tbl_name}
    WHERE `{x_fld_name}` IS NOT NULL
    AND `{y_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    cols = ['chart_val', 'series_val', 'x', 'y']
    df = pd.DataFrame(data, columns=cols)
    ## build result
    chart_series_xy_specs = []
    for chart_val in df['chart_val'].unique():
        series_xy_specs = []
        for series_val in df.loc[df['chart_val'] == chart_val, 'series_val'].unique():
            xys = df.loc[
                (df['chart_val'] == chart_val) & (df['series_val'] == series_val),
                ['x', 'y']
            ].to_records(index=False).tolist()
            series_xy_spec = SeriesXYSpec(
                lbl=series_vals2lbls.get(series_val, series_val),
                xys=xys,
            )
            series_xy_specs.append(series_xy_spec)
        chart_series_xy_spec = ChartSeriesXYSpec(
            lbl=f"{chart_fld_lbl}: {chart_vals2lbls.get(chart_val, chart_val)}",
            series_xy_specs=series_xy_specs,
        )
        chart_series_xy_specs.append(chart_series_xy_spec)
    result = ChartSeriesXYSpecs(
        chart_series_xy_specs=chart_series_xy_specs,
    )
    return result
