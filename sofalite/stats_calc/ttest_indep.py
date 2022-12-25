from sofalite.conf.data import ValDets
from sofalite.sql_extraction.db import ExtendedCursor
from sofalite.sql_extraction.utils import get_sample_numbers
from sofalite.stats_calc import conf as stats_conf, engine
from sofalite.utils.misc import todict

def get_results(cur: ExtendedCursor, tbl_name: str,
        grouping_fld_lbl: str, grouping_fld_name: str,
        group_a_dets: ValDets, group_b_dets: ValDets, grouping_val_is_numeric,
        measure_fld_lbl: str, measure_fld_name: str,
        tbl_filt_clause: str | None = None) -> stats_conf.TTestIndepResultExt:
    """
    Get independent t-test results.

    :param cur: sqlite extended cursor
    :param str tbl_name: name of table containing the data
    :param str tbl_filt_clause: clause ready to put after AND in a WHERE filter.
     E.g. WHERE ... AND age > 10
     Sometimes there is a global filter active in SOFA for a table e.g. age > 10,
     and we will need to apply that filter to ensure we are only getting the correct values
    :param str grouping_fld_lbl: e.g. the variable might be gender but the label might be Gender
    :param str grouping_fld_name: the grouping variable
     e.g. if we are interested in getting a sample of values for females
     then our grouping variable might be gender or sex
    :param grouping_fld_vals_dets: details of the values for the grouping variable (always two for t-test)
     e.g. if we are interested in getting a sample of values by gender
     then the first value might be 0 or 'male' and the label might be 'Male'
    :param bool grouping_val_is_numeric: so we know whether to quote it or not
    :param numeric measure_fld_lbl: e.g. Weight
    :param numeric measure_fld_name: e.g. weight
    """
    ## build samples ready for ttest_indep function
    sample_a_vals = get_sample_numbers(cur, tbl_name=tbl_name,
        grouping_filt_fld_name=grouping_fld_name,
        grouping_filt_val=group_a_dets.val,
        grouping_filt_val_is_numeric=grouping_val_is_numeric,
        measure_fld_name=measure_fld_name, tbl_filt_clause=tbl_filt_clause)
    sample_a = stats_conf.Sample(lbl=group_a_dets.lbl, vals=sample_a_vals)
    sample_b_vals = get_sample_numbers(cur, tbl_name=tbl_name,
        grouping_filt_fld_name=grouping_fld_name,
        grouping_filt_val=group_b_dets.val,
        grouping_filt_val_is_numeric=grouping_val_is_numeric,
        measure_fld_name=measure_fld_name, tbl_filt_clause=tbl_filt_clause)
    sample_b = stats_conf.Sample(lbl=group_b_dets.lbl, vals=sample_b_vals)
    ## get results
    ttest_indep_results = engine.ttest_ind(sample_a, sample_b)
    ttest_indep_results_extended = stats_conf.TTestIndepResultExt(**todict(ttest_indep_results),
        group_lbl=grouping_fld_lbl, measure_fld_lbl=measure_fld_lbl)
    return ttest_indep_results_extended
