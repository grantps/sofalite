"""
Get all vals by group, combine, and get overall bin_dets (discard overall bin_freqs).
Then, using get_bin_freqs(vals, bin_dets), and the common bin_dets, get bin_freqs for each chart.
"""
import pandas as pd

from sofalite.conf.charts.data.vals import HistoValsSpecs, HistoValsSpec
from sofalite.sql_extraction.db import ExtendedCursor

def by_vals(cur: ExtendedCursor, tbl_name: str,
        fld_name: str, fld_lbl: str,
        tbl_filt_clause: str | None = None) -> HistoValsSpec:
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{fld_name}` AS y
    FROM {tbl_name}
    WHERE `{fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    vals = [row[0] for row in data]
    ## build result
    data_spec = HistoValsSpec(
        chart_lbl=None,
        fld_lbl=fld_lbl,
        vals=vals,
    )
    return data_spec

def by_chart(cur: ExtendedCursor, tbl_name: str,
        chart_fld_name: str, chart_fld_lbl: str,
        fld_name: str, fld_lbl: str,
        chart_vals2lbls: dict | None,
        tbl_filt_clause: str | None = None) -> HistoValsSpecs:
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
      {chart_fld_name},
        `{fld_name}` AS
      y
    FROM {tbl_name}
    WHERE `{chart_fld_name}` IS NOT NULL
    AND `{fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    cols = ['chart_val', 'val']
    df = pd.DataFrame(data, columns=cols)
    chart_vals_specs = []
    for chart_val in df['chart_val'].unique():
        chart_lbl = chart_vals2lbls.get(chart_val, chart_val)
        df_vals = df.loc[df['chart_val'] == chart_val, ['val']]
        vals = list(df_vals['val'])
        vals_spec = HistoValsSpec(
            chart_lbl=chart_lbl,
            fld_lbl=fld_lbl,  ## needed when single chart but redundant / repeated here in multi-chart context
            vals=vals,
        )
        chart_vals_specs.append(vals_spec)
    data_spec = HistoValsSpecs(
        chart_fld_lbl=chart_fld_lbl,
        fld_lbl=fld_lbl,
        chart_vals_specs=chart_vals_specs,
    )
    return data_spec
