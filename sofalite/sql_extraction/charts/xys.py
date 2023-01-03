
from sofalite.sql_extraction.db import ExtendedCursor

def by_xy(cur: ExtendedCursor, tbl_name: str,
        x_fld_name: str, x_fld_lbl: str,
        y_fld_name: str, y_fld_lbl: str,
        tbl_filt_clause: str | None = None) -> XYSpecs:
    ...
