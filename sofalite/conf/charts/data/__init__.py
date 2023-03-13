"""
The job of these functions is to get all the details you could possibly want about the data -
including labels, amounts etc. - into a dataclass.

These dataclasses should have everything included that directly relates to the data - field labels, value labels etc.
They shouldn't contain any settings which are purely about style or display.

For example:
IN: chart_lbl
OUT: rotate_x_lbls, show_n_records, legend_lbl (as such - might actually be one of the data labels)
"""
