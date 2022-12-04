import logging
from typing import Sequence

from sofalite.conf.chart import (
    AVG_CHAR_WIDTH_PIXELS, AVG_LINE_HEIGHT_PIXELS, DOJO_Y_TITLE_OFFSET_0, MAX_SAFE_X_LBL_LEN_PIXELS,
    ChartDetails, LeftMarginOffsetDetails, XAxisSpec)

def get_left_margin_offset(*, width_after_left_margin: float, offsets: LeftMarginOffsetDetails,
        multi_chart: bool, y_title_offset: float, rotated_x_lbls: bool) -> int:
    wide = width_after_left_margin > 1_200
    initial_offset = offsets.wide_offset if wide else offsets.initial_offset  ## otherwise gets squeezed out e.g. in pct
    offset = initial_offset + y_title_offset - DOJO_Y_TITLE_OFFSET_0
    offset = offset + offsets.rotate_offset if rotated_x_lbls else offset
    offset = offset + offsets.multi_chart_offset if multi_chart else offset
    return offset

def get_x_font_size(*, n_x_items: int, multi_chart: bool) -> float:
    if n_x_items <= 5:
        x_font_size = 10
    elif n_x_items > 10:
        x_font_size = 8
    else:
        x_font_size = 9
    x_font_size = x_font_size * 0.75 if multi_chart else x_font_size
    return x_font_size

def get_height(*, axis_lbl_drop: float, rotated_x_lbls=False, max_x_lbl_length: float) -> float:
    height = 310
    if rotated_x_lbls:
        height += AVG_CHAR_WIDTH_PIXELS * max_x_lbl_length
    height += axis_lbl_drop  ## compensate for loss of bar display height
    return height

def get_axis_lbl_drop(*, multi_chart: bool, rotated_x_lbls: bool, max_lbl_lines: int) -> int:
    axis_lbl_drop = 10 if multi_chart else 15
    if not rotated_x_lbls:
        extra_lines = max_lbl_lines - 1
        axis_lbl_drop += AVG_LINE_HEIGHT_PIXELS * extra_lines
    logging.debug(axis_lbl_drop)
    return axis_lbl_drop

def get_y_title_offset(*, max_y_lbl_length: int, x_lbl_len: int, rotated_x_lbls=False) -> int:
    """
    Need to shift y-axis title left
    if wide y-axis label or first x-axis label is wide.
    """
    ## 45 is a good total offset with label width of 20
    y_title_offset = DOJO_Y_TITLE_OFFSET_0 - 20
    ## x-axis adjustment
    horiz_x_lbls = not rotated_x_lbls
    if horiz_x_lbls:
        if x_lbl_len * AVG_CHAR_WIDTH_PIXELS > MAX_SAFE_X_LBL_LEN_PIXELS:
            lbl_width_shifting = (x_lbl_len * AVG_CHAR_WIDTH_PIXELS) - MAX_SAFE_X_LBL_LEN_PIXELS
            lbl_shift = lbl_width_shifting / 2  ## half of label goes to the right
            y_title_offset += lbl_shift
    ## y-axis adjustment
    max_width_y_labels = (max_y_lbl_length * AVG_CHAR_WIDTH_PIXELS)
    logging.debug(f"{max_width_y_labels=}")
    y_title_offset += max_width_y_labels
    logging.debug(f"{y_title_offset=}")
    y_title_offset = max([y_title_offset, DOJO_Y_TITLE_OFFSET_0])
    return y_title_offset

def get_y_max(charts_dets: Sequence[ChartDetails]):
    all_y_vals = []
    for chart_dets in charts_dets:
        for series_det in chart_dets.series_dets:
            all_y_vals += series_det.y_vals
    max_all_y_vals = max(all_y_vals)
    y_max = max_all_y_vals * 1.1  ## slightly over just to be safe
    return y_max

def get_x_axis_lbl_dets(x_axis_specs: Sequence[XAxisSpec]) -> list[str]:
    """
    Note - can be a risk that a split label for the middle x value
    will overlap with x-axis label below
    """
    lbl_dets = []
    for n, x_axis_spec in enumerate(x_axis_specs, 1):
        val_lbl = x_axis_spec.lbl_split_into_lines
        lbl_dets.append(f'{{value: {n}, text: "{val_lbl}"}}')
    return lbl_dets
