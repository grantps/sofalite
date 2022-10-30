
"""
with con, cur etc
"""

def get_list(tbl, tbl_filt, flds, fld_measure,
        fld_filter, filter_val):
    """
    Get list of non-missing values in field. Must return list of floats. SQLite
    sometimes returns strings even though REAL data type. Not known why. Used,
    for example, in the independent samples t-test.

    :param str fld_filter: the grouping variable
    """
    fld_val_clause = getdata.make_fld_val_clause(
        dbe, flds, fld_filter, filter_val)
    objqtr = getdata.get_obj_quoter_func(dbe)
    unused, and_tbl_filt = lib.FiltLib.get_tbl_filts(tbl_filt)
    SQL_get_list = f"""SELECT {objqtr(fld_measure)}
        FROM {getdata.tblname_qtr(dbe, tbl)}
        WHERE {objqtr(fld_measure)} IS NOT NULL
        AND {fld_val_clause + and_tbl_filt}"""
    logging.debug(SQL_get_list)
    cur.execute(SQL_get_list)
    ## SQLite sometimes returns strings even if REAL
    lst = [float(x[0]) for x in cur.fetchall()]
    if len(lst) < 2:
        raise my_exceptions.TooFewValsInSamplesForAnalysis(fld_filter,
            filter_val)
    return lst
