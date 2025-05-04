from sofalite.data_extraction.db import ExtendedCursor
from sofalite.data_extraction.interfaces import ValSpec
from sofalite.data_extraction.utils import get_sample
from sofalite.stats_calc import interfaces as stats_interfaces, engine
from sofalite.utils.misc import todict

def get_results(cur: ExtendedCursor, tbl_name: str,
        grouping_fld_name: str, grouping_fld_lbl: str,
        group_a_val_spec: ValSpec, group_b_val_spec: ValSpec, grouping_val_is_numeric,
        measure_fld_name: str, measure_fld_lbl: str,
        tbl_filt_clause: str | None = None) -> stats_interfaces.TTestIndepResultExt:
    """
    Get independent t-test results.

    :param sqlite extended cursor
    :param tbl_name: name of table containing the data
    :param tbl_filt_clause: clause ready to put after AND in a WHERE filter.
     E.g. WHERE ... AND age > 10
     Sometimes there is a global filter active in SOFA for a table e.g. age > 10,
     and we will need to apply that filter to ensure we are only getting the correct values
    :param grouping_fld_lbl: e.g. the variable might be gender but the label might be Gender
    :param grouping_fld_name: the grouping variable
     e.g. if we are interested in getting a sample of values for females
     then our grouping variable might be gender or sex
    :param group_a_val_spec: details of the value of the grouping variable defining the first sample group
     e.g. if we are interested in getting a sample of values by gender
     then the first value might be 0 or 'male' and the label might be 'Male'
    :param group_b_val_spec: details of the value of the grouping variable defining the second sample group
    :param grouping_val_is_numeric: so we know whether to quote it or not
    :param measure_fld_lbl: e.g. Weight
    :param measure_fld_name: e.g. weight
    """
    ## build samples ready for ttest_indep function
    sample_a = get_sample(cur, tbl_name=tbl_name,
        grouping_filt_fld_name=grouping_fld_name,
        grouping_filt_val_spec=group_a_val_spec,
        grouping_filt_val_is_numeric=grouping_val_is_numeric,
        measure_fld_name=measure_fld_name, tbl_filt_clause=tbl_filt_clause)
    sample_b = get_sample(cur, tbl_name=tbl_name,
        grouping_filt_fld_name=grouping_fld_name,
        grouping_filt_val_spec=group_b_val_spec,
        grouping_filt_val_is_numeric=grouping_val_is_numeric,
        measure_fld_name=measure_fld_name, tbl_filt_clause=tbl_filt_clause)
    ## get results
    ttest_indep_results = engine.ttest_ind(sample_a, sample_b)
    ttest_indep_results_extended = stats_interfaces.TTestIndepResultExt(**todict(ttest_indep_results),
        group_lbl=grouping_fld_lbl, measure_fld_lbl=measure_fld_lbl)
    return ttest_indep_results_extended
