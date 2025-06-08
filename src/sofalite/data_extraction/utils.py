from sofalite.conf.main import DbeName, DbeSpec
from sofalite.data_extraction.db import ExtendedCursor
from sofalite.data_extraction.interfaces import ValSpec
from sofalite.stats_calc.interfaces import PairedData, Sample

def get_paired_data(*, cur: ExtendedCursor, dbe_spec: DbeSpec, src_tbl_name: str,
        variable_a_name: str, variable_b_name: str,
        tbl_filt_clause: str | None = None, unique=False) -> PairedData:
    """
    For each field, returns a list of all non-missing values where there is also
    a non-missing value in the other field. Used in, for example, the paired
    samples t-test.

    Args:
        unique: if True only look at unique pairs. Useful for scatter plotting.
    """
    and_tbl_filt_clause = f"AND {tbl_filt_clause}" if tbl_filt_clause else ''
    src_tbl_name_quoted = dbe_spec.entity_quoter(src_tbl_name)
    variable_a_name_quoted = dbe_spec.entity_quoter(variable_a_name)
    variable_b_name_quoted = dbe_spec.entity_quoter(variable_b_name)
    if unique:
        sql_get_pairs = f"""\
        SELECT {variable_a_name_quoted }, {variable_b_name_quoted}
        FROM {src_tbl_name_quoted}
        WHERE {variable_a_name_quoted } IS NOT NULL
        AND {variable_b_name_quoted} IS NOT NULL {and_tbl_filt_clause}
        GROUP BY {variable_a_name_quoted }, {variable_b_name_quoted}"""
    else:
        sql_get_pairs = f"""\
        SELECT {variable_a_name_quoted }, {variable_b_name_quoted}
        FROM {src_tbl_name_quoted}
        WHERE {variable_a_name_quoted } IS NOT NULL
        AND {variable_b_name_quoted} IS NOT NULL {and_tbl_filt_clause}"""
    cur.exe(sql_get_pairs)
    a_b_val_tuples = cur.fetchall()
    ## SQLite sometimes returns strings even if REAL
    variable_a_vals = [float(x[0]) for x in a_b_val_tuples]
    variable_b_vals = [float(x[1]) for x in a_b_val_tuples]
    return PairedData(
        variable_a_vals=variable_a_vals,
        variable_b_vals=variable_b_vals,
    )

def get_sample(*, cur: ExtendedCursor, dbe_spec: DbeSpec, src_tbl_name: str,
        grouping_filt_fld_name: str, grouping_filt_val_spec: ValSpec, grouping_filt_val_is_numeric: bool,
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
    :param src_tbl_name: name of table containing the data
    :param tbl_filt_clause: clause ready to put after AND in a WHERE filter.
     E.g. WHERE ... AND age > 10
     Sometimes there is a global filter active in SOFA for a table e.g. age > 10,
     and we will need to apply that filter to ensure we are only getting the correct values
    :param grouping_filt_fld_name: the grouping variable
     e.g. if we are interested in getting a sample of values for females
     then our grouping variable might be gender or sex
    :param grouping_filt_val_spec: the val spec for the grouping variable (lbl and val)
     e.g. if we are interested in getting a sample of values for females
     then our value might be 2 or 'female'
    :param grouping_filt_val_is_numeric: so we know whether to quote it or not
    :param measure_fld_name: e.g. weight
    """
    ## prepare items
    and_tbl_filt_clause = f"AND {tbl_filt_clause}" if tbl_filt_clause else ''
    if grouping_filt_val_is_numeric:
        grouping_filt_clause = f"{grouping_filt_fld_name} = {grouping_filt_val_spec.val}"
    else:
        grouping_filt_clause = f"{grouping_filt_fld_name} = '{grouping_filt_val_spec.val}'"
    and_grouping_filt_clause = f"AND {grouping_filt_clause}"
    src_tbl_name_quoted = dbe_spec.entity_quoter(src_tbl_name)
    measure_fld_name_quoted = dbe_spec.entity_quoter(measure_fld_name)
    ## assemble SQL
    sql = f"""
    SELECT {measure_fld_name_quoted}
    FROM {src_tbl_name_quoted}
    WHERE {measure_fld_name_quoted} IS NOT NULL
    {and_tbl_filt_clause}
    {and_grouping_filt_clause}
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    sample_vals = [row[0] for row in data]
    ## coerce into floats because SQLite sometimes returns strings even if REAL TODO: reuse coerce logic and desc
    if dbe_spec.dbe_name == DbeName.SQLITE:
        sample_vals = [float(val) for val in sample_vals]
    if len(sample_vals) < 2:
        raise Exception(f"Too few {measure_fld_name} values in sample for analysis "
            f"when getting sample for {grouping_filt_clause}")
    sample = Sample(lbl=grouping_filt_val_spec.lbl, vals=sample_vals)
    return sample
