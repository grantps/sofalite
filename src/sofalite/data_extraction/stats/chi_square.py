from collections.abc import Sequence
from collections import defaultdict
from itertools import product

from numpy import reshape

from sofalite import logger
from sofalite.conf.main import (
    MAX_CHI_SQUARE_VALS_IN_DIM, MAX_CHI_SQUARE_CELLS, MAX_VALUE_LENGTH_IN_SQL_CLAUSE, MIN_CHI_SQUARE_VALS_IN_DIM,
    DbeName, DbeSpec)
from sofalite.data_extraction.db import ExtendedCursor
from sofalite.data_extraction.stats.interfaces import ChiSquareData
from sofalite.stats_calc import engine
from sofalite.stats_calc.interfaces import ChiSquareResult, ChiSquareWorkedResultCellData, ChiSquareWorkedResultData

def get_fractions_of_total_for_variable(*, cur: ExtendedCursor, dbe_spec: DbeSpec,
        src_tbl_name: str, tbl_filt_clause: str, variable_name: str, other_variable_name: str) -> list[float]:
    """
    Looking at the frequencies for each value in the variable, what fractional share does that value have of the total?
    For example, if the numbers are 5, 8, and 7 for young, middle, and old
    then the fractions are .25, .40, .35
    When calculating the frequencies for the variable,
    leave out any rows in the source data where either the variable or the other variable are missing.
    We are only counting frequencies for each intersection of values (non-NULL).
    """
    ## prepare items
    quoted_src_tbl_name = dbe_spec.entity_quoter(src_tbl_name)
    quoted_variable_name = dbe_spec.entity_quoter(variable_name)
    quoted_other_variable_name = dbe_spec.entity_quoter(other_variable_name)
    ## get data
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    sql_get_fractions = f"""\
    SELECT {quoted_variable_name}, COUNT(*) AS n
    FROM {quoted_src_tbl_name} 
    WHERE {quoted_variable_name} IS NOT NULL AND {quoted_other_variable_name} IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY {quoted_variable_name}
    ORDER BY {quoted_variable_name}
    """
    logger.debug(sql_get_fractions)
    cur.exe(sql_get_fractions)
    lst_counts = []
    total = 0
    for data_tuple in cur.fetchall():
        val = data_tuple[1]
        lst_counts.append(val)
        total += val
    lst_fracs = [( x / float(total)) for x in lst_counts]
    return lst_fracs

def get_cleaned_values(*, original_vals: list[str | float], dbe_spec: DbeSpec) -> list[str | float]:
    """
    Get values ready to use. Check there are no excessively long labels.
    """
    if dbe_spec.dbe_name == DbeName.SQLITE:
        ## SQLite sometimes returns strings even if REAL
        try:
            vals = [float(val) for val in original_vals]
            return vals
        except ValueError:
            pass  ## leave them as strings
    ## if strings, check not too long
    for val in original_vals:
        if len(val) > MAX_VALUE_LENGTH_IN_SQL_CLAUSE:
            raise ValueError(f"'{val}' is too long to be used as a category value "
                f"({len(val)} > maximum value setting: {MAX_VALUE_LENGTH_IN_SQL_CLAUSE})")
    return original_vals

def get_chi_square_data(*, cur: ExtendedCursor, dbe_spec: DbeSpec, src_tbl_name: str, tbl_filt_clause: str,
        variable_a_name: str, variable_b_name: str) -> ChiSquareData:
    """
    The Chi Square statistical calculation relies on having access to the raw counts per intersection between
    variable A and B. These are the observed values. E.g.

             Badminton | Basketball | Football | Tennis
    ---------------------------------------------------
    Korea          100           10        150        0  <=== note - all cells must be filled (0 if no rows in particular intersection of A and B values)
    NZ              15           25         25       25
    USA            100          500        150      250

    There is then a calculation of the expected values for each intersection.
    These values are calculated so that the distribution within, for example, sports, is the same for each country.
    In other words, as if there were no relationship between country and sport.
    Later on, we will look at the difference between the actual, observed values and the matching expected values.
    The important thing with the lists of actual and observed values is that they are in the same order as each other
    so they can be compared to calculate how large a difference there is between them.
    The lists are B within A (e.g. a1b1, a1b2, a1b3, a2b1, a2b2 ...) but the nature of the ordering doesn't matter,
    only the fact that it is the same between the observed and expected lists.
    Also required are some other attributes of the result, e.g. minimum cell count, that are needed to
    handle and interpret the result of the statistical calculation.
    """
    ## prepare items
    quoted_src_tbl_name = dbe_spec.entity_quoter(src_tbl_name)
    quoted_variable_a_name = dbe_spec.entity_quoter(variable_a_name)
    quoted_variable_b_name = dbe_spec.entity_quoter(variable_b_name)
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## A) get ROW vals used ***********************
    sql_row_vals_used = f"""\
    SELECT {quoted_variable_a_name}
    FROM {quoted_src_tbl_name}
    WHERE {quoted_variable_a_name} IS NOT NULL AND {quoted_variable_b_name} IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY {quoted_variable_a_name}
    ORDER BY {quoted_variable_a_name}
    """
    cur.exe(sql_row_vals_used)
    row_data = cur.fetchall()
    row_vals = [x[0] for x in row_data]
    variable_a_values = get_cleaned_values(original_vals=row_vals, dbe_spec=dbe_spec)
    n_variable_a_vals = len(variable_a_values)
    if n_variable_a_vals > MAX_CHI_SQUARE_VALS_IN_DIM:
        raise Exception(f"Too many separate values ({n_variable_a_vals} vs "
            f"maximum allowed of {MAX_CHI_SQUARE_VALS_IN_DIM}) in variable '{quoted_variable_a_name}'")
    if n_variable_a_vals < MIN_CHI_SQUARE_VALS_IN_DIM:
        raise Exception(f"Not enough separate values ({n_variable_a_vals} vs "
            f"minimum allowed of {MIN_CHI_SQUARE_VALS_IN_DIM}) in variable '{quoted_variable_a_name}'")
    ## B) get COL vals used (almost a repeat) ***********************
    sql_col_vals_used = f"""\
    SELECT {quoted_variable_b_name}
    FROM {quoted_src_tbl_name}
    WHERE {quoted_variable_a_name} IS NOT NULL AND {quoted_variable_b_name} IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY {quoted_variable_b_name}
    ORDER BY {quoted_variable_b_name}
    """
    cur.exe(sql_col_vals_used)
    col_data = cur.fetchall()
    col_vals = [x[0] for x in col_data]
    variable_b_values = get_cleaned_values(original_vals=col_vals, dbe_spec=dbe_spec)
    n_variable_b_vals = len(variable_b_values)
    if n_variable_b_vals > MAX_CHI_SQUARE_VALS_IN_DIM:
        raise Exception(f"Too many separate values ({n_variable_b_vals} vs "
            f"maximum allowed of {MAX_CHI_SQUARE_VALS_IN_DIM}) in variable '{quoted_variable_b_name}'")
    if n_variable_b_vals < MIN_CHI_SQUARE_VALS_IN_DIM:
        raise Exception(f"Not enough separate values ({n_variable_b_vals} vs "
            f"minimum allowed of {MIN_CHI_SQUARE_VALS_IN_DIM}) in variable '{quoted_variable_b_name}'")
    ## C) combine results of A) and B) ***********************
    n_cells = len(variable_a_values) * len(variable_b_values)
    if n_cells > MAX_CHI_SQUARE_CELLS:
        raise Exception(f"Too many cells in Chi Square cross tab ({n_cells:,} "
            f"vs maximum allowed of {MAX_CHI_SQUARE_CELLS:,})")
    ## Build SQL to get all observed values (for each A, through B's)
    ## This order is useful when running row by row into an HTML table
    ## Get frequency per A and B intersection
    sql_get_observed_freqs_bits = ['SELECT ', ]
    freq_per_a_b_intersection_clauses_bits = []
    ## need to filter by vals within SQL so may need quoting observed values etc
    for val_a, val_b in product(variable_a_values, variable_b_values):
        quoted_val_a = dbe_spec.str_value_quoter(val_a)
        quoted_val_b = dbe_spec.str_value_quoter(val_b)
        clause = (
            f"SUM(CASE WHEN {quoted_variable_a_name} = {quoted_val_a} AND {quoted_variable_b_name} = {quoted_val_b} "
            "THEN 1 ELSE 0 END)")
        freq_per_a_b_intersection_clauses_bits.append(clause)
    freq_per_a_b_intersection_clauses = ',\n'.join(freq_per_a_b_intersection_clauses_bits)
    sql_get_observed_freqs_bits.append(freq_per_a_b_intersection_clauses)
    sql_get_observed_freqs_bits.append(f"FROM {quoted_src_tbl_name}")
    if tbl_filt_clause:
        sql_get_observed_freqs_bits.append(f"WHERE {tbl_filt_clause}")
    sql_get_observed_freqs = '\n'.join(sql_get_observed_freqs_bits)
    logger.debug(f"{sql_get_observed_freqs=}")
    cur.exe(sql_get_observed_freqs)
    observed_values_a_then_b_ordered = cur.fetchone()
    if not observed_values_a_then_b_ordered:
        raise Exception("No observed values")
    observed_values_a_then_b_ordered = list(observed_values_a_then_b_ordered)
    logger.debug(f"{observed_values_a_then_b_ordered=}")
    total_observed_values = float(sum(observed_values_a_then_b_ordered))
    ## expected values
    fractions_of_total_for_variable_a = get_fractions_of_total_for_variable(
        cur=cur, dbe_spec=dbe_spec, src_tbl_name=src_tbl_name, tbl_filt_clause=tbl_filt_clause,
        variable_name=variable_a_name, other_variable_name=variable_b_name)
    fractions_of_total_for_variable_b = get_fractions_of_total_for_variable(
        cur=cur, dbe_spec=dbe_spec, src_tbl_name=src_tbl_name, tbl_filt_clause=tbl_filt_clause,
        variable_name=variable_b_name, other_variable_name=variable_a_name)
    degrees_of_freedom = (n_variable_a_vals - 1) * (n_variable_b_vals - 1)
    expected_values_a_then_b_ordered = []
    for fraction_of_val_in_variable_a, fraction_of_val_in_variable_b in product(
            fractions_of_total_for_variable_a, fractions_of_total_for_variable_b):
        expected_values_a_then_b_ordered.append(fraction_of_val_in_variable_a * fraction_of_val_in_variable_b * total_observed_values)
    logger.debug(f"{expected_values_a_then_b_ordered=}")
    if len(observed_values_a_then_b_ordered) != len(expected_values_a_then_b_ordered):
        raise Exception('Different number of observed and expected values. '
            f'{len(observed_values_a_then_b_ordered)} vs {len(expected_values_a_then_b_ordered)}')
    minimum_cell_count = min(expected_values_a_then_b_ordered)
    cells_freq_under_5 = [x for x in expected_values_a_then_b_ordered if x < 5]
    pct_cells_freq_under_5 = (100 * len(cells_freq_under_5)) / float(len(expected_values_a_then_b_ordered))
    return ChiSquareData(
        variable_a_values=variable_a_values,
        variable_b_values=variable_b_values,
        observed_values_a_then_b_ordered=observed_values_a_then_b_ordered,
        expected_values_a_then_b_ordered=expected_values_a_then_b_ordered,
        minimum_cell_count=minimum_cell_count,
        pct_cells_freq_under_5=pct_cells_freq_under_5,
        degrees_of_freedom=degrees_of_freedom,
    )

def get_worked_result_data(*, variable_a_values: Sequence[int | str], variable_b_values: Sequence[int | str],
        observed_values_a_then_b_ordered: Sequence[float],
        degrees_of_freedom: int) -> ChiSquareWorkedResultData:
    n_a = len(variable_a_values)
    n_b = len(variable_b_values)
    ## Restructure observed_values_a_then_b_ordered to nested lists following pattern of contingency table
    ## The lists are b within a e.g. a1b1, a1b2, a1b3, a2b1, a2b2 ...
    ## (i.e. across the rows)
    obs = reshape(observed_values_a_then_b_ordered, (n_a, n_b))
    grand_total = sum(observed_values_a_then_b_ordered)
    row_n2row_sum = defaultdict(int)
    col_n2col_sum = defaultdict(int)
    row_n2obs_row = defaultdict(list)
    col_n2obs_row = defaultdict(list)
    coord2observed = dict()
    ## round 1
    for col_n, _val_b in enumerate(variable_b_values, 1):
        for row_n, _val_a in enumerate(variable_a_values, 1):
            observed_value = int(obs[row_n - 1][col_n - 1])  ## need zero-based indexing for numpy to get our individual value
            row_n2row_sum[row_n] += observed_value
            col_n2col_sum[col_n] += observed_value
            row_n2obs_row[row_n].append(observed_value)
            col_n2obs_row[col_n].append(observed_value)
            coord2observed[(row_n, col_n)] = observed_value  ## can't add any more details until calculated row and column totals
    ## round 2 (now that we have row and column totals we can calculate the missing bits)
    cells_data = {}
    pre_chis = []
    chi_square = 0
    for coord, observed_value in coord2observed.items():
        row_n, col_n = coord
        row_sum = row_n2row_sum[row_n]
        col_sum = col_n2col_sum[col_n]
        expected_value = (row_sum * col_sum) / float(grand_total)
        min_of_observed_and_expected = min([observed_value, expected_value])
        max_of_observed_and_expected = max([observed_value, expected_value])
        diff_of_min_and_max = max_of_observed_and_expected - min_of_observed_and_expected
        diff_of_min_and_max = round(diff_of_min_and_max, 3)
        min_of_observed_and_expected = round(min_of_observed_and_expected, 3)
        max_of_observed_and_expected = round(max_of_observed_and_expected, 3)
        diff_squared = round(diff_of_min_and_max ** 2, 3)
        raw_pre_chi = diff_squared / float(expected_value)
        chi_square += raw_pre_chi
        pre_chi = round(raw_pre_chi, 3)
        pre_chis.append(pre_chi)
        cell_data = ChiSquareWorkedResultCellData(
            observed_value=observed_value,
            row_sum=row_sum,
            col_sum=col_sum,
            expected_value=round(expected_value, 3),
            min_of_observed_and_expected=min_of_observed_and_expected,
            max_of_observed_and_expected=max_of_observed_and_expected,
            diff_of_min_and_max=diff_of_min_and_max,
            diff_squared=diff_squared,
            pre_chi=pre_chi,
        )
        cells_data[coord] = cell_data
    return ChiSquareWorkedResultData(
        grand_tot=grand_total,
        row_n2row_sum=row_n2row_sum,
        row_n2obs_row=row_n2obs_row,
        col_n2col_sum=col_n2col_sum,
        col_n2obs_row=col_n2obs_row,
        row_n=n_a,
        col_n=n_b,
        row_n_minus_1=n_a - 1,
        col_n_minus_1=n_b - 1,
        cells_data=cells_data,
        pre_chis=pre_chis,
        chi_square=chi_square,
        degrees_of_freedom=degrees_of_freedom,
    )

def get_results(cur: ExtendedCursor, dbe_spec: DbeSpec, src_tbl_name: str,
        variable_a_name: str, variable_b_name: str,
        tbl_filt_clause: str | None = None, *, show_workings=False) -> ChiSquareResult:
    chi_square_data = get_chi_square_data(cur=cur, dbe_spec=dbe_spec,
        src_tbl_name=src_tbl_name, tbl_filt_clause=tbl_filt_clause,
        variable_a_name=variable_a_name, variable_b_name=variable_b_name)
    ## get results
    chi_square, p = engine.chisquare(
        f_obs=chi_square_data.observed_values_a_then_b_ordered, f_exp=chi_square_data.expected_values_a_then_b_ordered,
        df=chi_square_data.degrees_of_freedom)
    if show_workings:
        chi_square_worked_result_data = get_worked_result_data(
            variable_a_values=chi_square_data.variable_a_values, variable_b_values=chi_square_data.variable_b_values,
            observed_values_a_then_b_ordered=chi_square_data.observed_values_a_then_b_ordered,
            degrees_of_freedom=chi_square_data.degrees_of_freedom)
    else:
        chi_square_worked_result_data = None
    return ChiSquareResult(
        variable_a_name=variable_a_name, variable_b_name=variable_b_name,
        variable_a_values=chi_square_data.variable_a_values, variable_b_values=chi_square_data.variable_b_values,
        observed_values_a_then_b_ordered=chi_square_data.observed_values_a_then_b_ordered,
        expected_values_a_then_b_ordered=chi_square_data.expected_values_a_then_b_ordered,
        p=p, chi_square=chi_square, degrees_of_freedom=chi_square_data.degrees_of_freedom,
        minimum_cell_count=chi_square_data.minimum_cell_count, pct_cells_lt_5=chi_square_data.pct_cells_freq_under_5,
        chi_square_worked_result_data=chi_square_worked_result_data,
    )
