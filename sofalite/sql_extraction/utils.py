from sofalite.sql_extraction.db import ExtendedCursor

def get_sample_numbers(cur: ExtendedCursor,
        tbl_name: str,
        grouping_filt_fld_name: str, grouping_filt_val, grouping_filt_val_is_numeric,
        measure_fld_name: str,
        tbl_filt_clause: str | None = None) -> list[float]:
    """
    Get list of non-missing values in numeric measure field for a group defined by another field
    e.g. getting weights for males.
    Must return list of floats.
    SQLite sometimes returns strings even though REAL data type. Not known why.
    Used, for example, in the independent samples t-test.
    Note - various filters might apply e.g. we want a sample for male weight
    but only where age > 10

    :param cur: sqlite extended cursor
    :param str tbl_name: name of table containing the data
    :param str tbl_filt_clause: clause ready to put after AND in a WHERE filter.
     E.g. WHERE ... AND age > 10
     Sometimes there is a global filter active in SOFA for a table e.g. age > 10,
     and we will need to apply that filter to ensure we are only getting the correct values
    :param str grouping_filt_fld_name: the grouping variable
     e.g. if we are interested in getting a sample of values for females
     then our grouping variable might be gender or sex
    :param grouping_filt_val: the value for the grouping variable
     e.g. if we are interested in getting a sample of values for females
     then our value might be 2 or 'female'
    :param bool grouping_filt_val_is_numeric: so we know whether to quote it or not
    :param numeric measure_fld_name: e.g. weight
    """
    ## prepare clauses
    and_tbl_filt_clause = f"AND {tbl_filt_clause}" if tbl_filt_clause else ''
    if grouping_filt_val_is_numeric:
        grouping_filt_clause = f"{grouping_filt_fld_name} = {grouping_filt_val}"
    else:
        grouping_filt_clause = f"{grouping_filt_fld_name} = '{grouping_filt_val}'"
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
    sample_numbers = [float(x[0]) for x in data]
    if len(sample_numbers) < 2:
        raise Exception(f"Too few {measure_fld_name} values in sample for analysis "
            f"when getting sample for {grouping_filt_clause}")
    return sample_numbers
