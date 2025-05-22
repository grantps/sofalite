from collections.abc import Sequence

from sofalite import logger
from sofalite.data_extraction.db import ExtendedCursor
from sofalite.data_extraction.interfaces import ValSpec
from sofalite.stats_calc import interfaces as stats_interfaces, engine

def get_obs_exp(cur, tbl, tbl_filt, where_tbl_filt, and_tbl_filt, flds, fld_a, fld_b):
    """
    Get list of observed and expected values ready for inclusion in Pearson's Chi Square test.

    NB must return 0 if nothing. All cells must be filled.

    Returns lst_obs, lst_exp, min_count, perc_cells_lt_5, df.

    NB some dbes return integers and some return Decimals.

    The lists are b within a e.g. a1b1, a1b2, a1b3, a2b1, a2b2 ...
    """
    ## A) get ROW vals used ***********************
    SQL_row_vals_used = f"""\
    SELECT {qfld_a}
    FROM {tbl}
    WHERE {qfld_b} IS NOT NULL AND {qfld_a} IS NOT NULL
    {and_tbl_filt}
    GROUP BY {qfld_a}
    ORDER BY {qfld_a}
    """
    cur.exe(SQL_row_vals_used)
    row_vals_used = cur.fetchall()
    vals_a = get_unique_dim_vals(row_vals_used, dbe, flds, fld_a)
    if len(vals_a) > mg.MAX_CHI_DIMS:
        raise my_exceptions.TooManyRowsInChiSquare
    if len(vals_a) < mg.MIN_CHI_DIMS:
        raise my_exceptions.TooFewRowsInChiSquare
    ## B) get COL vals used (almost a repeat) ***********************
    SQL_col_vals_used = f"""\
    SELECT {qfld_b}
    FROM {qtbl}
    WHERE {qfld_a} IS NOT NULL AND {qfld_b} IS NOT NULL
    {and_tbl_filt}
    GROUP BY {qfld_b}
    ORDER BY {qfld_b}
    """
    cur.exe(SQL_col_vals_used)
    col_vals_used = cur.fetchall()
    vals_b = get_unique_dim_vals(col_vals_used, dbe, flds, fld_b)
    if len(vals_b) > mg.MAX_CHI_DIMS:
        raise my_exceptions.TooManyColsInChiSquare
    if len(vals_b) < mg.MIN_CHI_DIMS:
        raise my_exceptions.TooFewColsInChiSquare
    if len(vals_a)*len(vals_b) > mg.MAX_CHI_CELLS:
        raise my_exceptions.TooManyCellsInChiSquare
    ## C) combine results of A) and B) ***********************
    ## build SQL to get all observed values (for each a, through b's)
    SQL_get_obs = 'SELECT '
    sql_lst = []
    ## need to filter by vals within SQL so may need quoting observed values etc
    for val_a in vals_a:
        val_quoter_a = get_val_quoter(dbe, flds, fld_a, val_a)
        for val_b in vals_b:
            val_quoter_b = get_val_quoter(dbe, flds, fld_b, val_b)
            clause = (f'\nSUM(CASE WHEN {qfld_a} = {val_quoter_a(val_a)} '
                f'AND {qfld_b} = {val_quoter_b(val_b)} THEN 1 ELSE 0 END)')
            sql_lst.append(clause)
    SQL_get_obs += ', '.join(sql_lst)
    SQL_get_obs += f'\nFROM {qtbl} '
    SQL_get_obs += f'\n{where_tbl_filt} '
    logger.debug(SQL_get_obs)
    cur.exe(SQL_get_obs)
    tup_obs = cur.fetchall()[0]
    if not tup_obs:
        raise Exception('No observed values')
    else:
        logger.debug(tup_obs)
    lst_obs = list(tup_obs)
    logger.debug(f'lst_obs: {lst_obs}')
    obs_total = float(sum(lst_obs))
    ## expected values
    lst_fracs_a = get_fracs(cur, tbl_filt, qtbl, qfld_a, qfld_b)
    lst_fracs_b = get_fracs(cur, tbl_filt, qtbl, qfld_b, qfld_a)
    df = (len(lst_fracs_a)-1)*(len(lst_fracs_b)-1)
    lst_exp = []
    for frac_a in lst_fracs_a:
        for frac_b in lst_fracs_b:
            lst_exp.append(frac_a*frac_b*obs_total)
    logger.debug(f'lst_exp: {lst_exp}')
    if len(lst_obs) != len(lst_exp):
        raise Exception('Different number of observed and expected values. '
            f'{len(lst_obs)} vs {len(lst_exp)}')
    min_count = min(lst_exp)
    lst_lt_5 = [x for x in lst_exp if x < 5]
    perc_cells_lt_5 = (100 * len(lst_lt_5)) / float(len(lst_exp))
    return vals_a, vals_b, lst_obs, lst_exp, min_count, perc_cells_lt_5, df


def get_results(cur: ExtendedCursor, src_tbl_name: str,
        grouping_fld_lbl: str, grouping_fld_name: str,
        grouping_fld_vals_spec: Sequence[ValSpec], grouping_val_is_numeric,
        measure_fld_lbl: str, measure_fld_name: str,
        tbl_filt_clause: str | None = None,
        high_precision_required=False) -> stats_interfaces.ChiSquareResult:

    ## get results
    chi_square_results = engine.chisquare(f_obs, f_exp, df=len(f_obs - 1))  ## df = degree of freedom

    return stats_interfaces.ChiSquareResult()
