from itertools import groupby  ## actually quite performant

from sofalite.conf.charts.data.freq_specs import CategoryValsSpec, CategoryValsSpecs
from sofalite.conf.misc import SortOrder
from sofalite.sql_extraction.db import ExtendedCursor

def by_category(cur: ExtendedCursor, tbl_name: str,
        fld_name: str,
        category_fld_name: str, category_fld_lbl: str, category_vals2lbls: dict | None = None,
        tbl_filt_clause: str | None = None,
        category_sort_order: SortOrder = SortOrder.VALUE) -> CategoryValsSpecs:
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{category_fld_name}` AS
      category_val,
      `{fld_name}`
    FROM {tbl_name}
    WHERE `{category_fld_name}` IS NOT NULL
    AND `{fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    ORDER BY `{category_fld_name}`, `{fld_name}`
    """
    ## get data
    cur.exe(sql)
    sorted_data = cur.fetchall()
    ## build result
    category_vals_specs = []
    for category_val, raw_vals in groupby(sorted_data, lambda t: t[0]):
        vals = list(raw_vals)
        category_vals_spec = CategoryValsSpec(
            category_val=category_val, category_val_lbl=category_vals2lbls.get(category_val, str(category_val)),
            vals=vals,
        )
        category_vals_specs.append(category_vals_spec)
    result = CategoryValsSpecs(
        category_fld_lbl=category_fld_lbl,
        category_vals_specs=category_vals_specs,
        category_sort_order=category_sort_order,
    )
    return result
