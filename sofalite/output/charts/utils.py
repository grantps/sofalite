import logging

from sofalite.conf.chart import (
    AVG_CHAR_WIDTH_PIXELS, AVG_LINE_HEIGHT_PIXELS, DOJO_Y_TITLE_OFFSET_0,
    ChartDetails, XAxisDetails)

def get_axis_lbl_drop(multi_chart: bool, rotate: bool, max_lbl_lines: int) -> int:
    axis_lbl_drop = 10 if multi_chart else 15
    if not rotate:
        extra_lines = max_lbl_lines - 1
        axis_lbl_drop += AVG_LINE_HEIGHT_PIXELS * extra_lines
    logging.debug(axis_lbl_drop)
    return axis_lbl_drop

def get_y_title_offset(
        max_y_lbl_len: int, x_lbl_len: int, max_safe_x_lbl_len_pixels: int, *,
        rotate=False) -> int:
    """
    Need to shift y-axis title left
    if wide y-axis label or first x-axis label is wide.
    """
    ## 45 is a good total offset with label width of 20
    y_title_offset = DOJO_Y_TITLE_OFFSET_0 - 20
    ## x-axis adjustment
    if not rotate:
        if x_lbl_len * AVG_CHAR_WIDTH_PIXELS > max_safe_x_lbl_len_pixels:
            lbl_width_shifting = (x_lbl_len * AVG_CHAR_WIDTH_PIXELS) - max_safe_x_lbl_len_pixels
            lbl_shift = lbl_width_shifting / 2  ## half of label goes to the right
            y_title_offset += lbl_shift
    ## y-axis adjustment
    max_width_y_labels = (max_y_lbl_len * AVG_CHAR_WIDTH_PIXELS)
    logging.debug(f"{max_width_y_labels=}")
    y_title_offset += max_width_y_labels
    logging.debug(f"{y_title_offset=}")
    y_title_offset = max([y_title_offset, DOJO_Y_TITLE_OFFSET_0])
    return y_title_offset

def get_y_max(charts_dets: ChartDetails):
    all_y_vals = []
    for chart_dets in charts_dets:
        for series_det in chart_dets.series_dets:
            all_y_vals += series_det.y_vals
    max_all_y_vals = max(all_y_vals)
    y_max = max_all_y_vals * 1.1  ## slightly over just to be safe
    return y_max

def get_x_axis_lbl_dets(x_axis_dets: XAxisDetails) -> list[str]:
    """
    Note - can be a risk that a split label for the middle x value
    will overlap with x-axis label below
    """
    lbl_dets = []
    for n, x_axis_det in enumerate(x_axis_dets, 1):
        val_lbl = x_axis_det.lbl_split_into_lines
        lbl_dets.append(f'{{value: {n}, text: "{val_lbl}"}}')
    return lbl_dets
