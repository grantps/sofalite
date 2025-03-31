"""
https://matplotlib.org/matplotblog/posts/pyplot-vs-object-oriented-interface/
"""
import logging
from typing import Sequence

from matplotlib import rcParams as mpl_settings
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from sofalite.conf.charts.misc import HistogramConf, HistogramData, ScatterplotConf,ScatterplotSeries
from sofalite.stats_calc.histogram import get_bin_details_from_vals
from sofalite.conf.stats.engine import get_normal_ys, get_regression_dets

def set_gen_mpl_settings(axes_lbl_size=14, xtick_lbl_size=10, ytick_lbl_size=10):
    mpl_settings['axes.labelsize'] = axes_lbl_size
    mpl_settings['xtick.labelsize'] = xtick_lbl_size
    mpl_settings['ytick.labelsize'] = ytick_lbl_size

def get_histogram_fig(chart_conf: HistogramConf, data_dets: HistogramData) -> Figure:
    """
    Start by getting nice initial bins bounds
    (without looking at the actual individual values and frequencies per bin yet).
    Based entirely on the min and max values.

    Then translate into details needed to actually make histogram esp frequencies per bin.

    Then try to fix any saw-toothing detected if it is possible.
    Requires enough bins to be able to reduce them and recalculate.
    """
    fig, ax = plt.subplots()
    rect = ax.patch
    rect.set_facecolor(chart_conf.inner_bg_colour)
    vals = data_dets.vals
    bin_dets, bin_freqs = get_bin_details_from_vals(vals)
    ax.set_xlabel(chart_conf.var_lbl)
    ax.set_ylabel('P')
    if chart_conf.chart_lbl:
        chart_lbl = chart_conf.chart_lbl
    else:
        chart_lbl = f"Histogram for {chart_conf.var_lbl}"
    ax.set_title(chart_lbl)
    ## see entry for hist in http://matplotlib.sourceforge.net/api/axes_api.html
    ## density=True means the integral of the histogram is 1 (the area = 1)
    ## the wider the bins the smaller the P values
    ## See https://plotly.com/chart-studio-help/histogram/
    ## See also https://matplotlib.org/stable/gallery/statistics/histogram_features.html
    n, bins, patches = ax.hist(vals, bin_dets.n_bins, density=True,
        range=(bin_dets.lower_limit, bin_dets.upper_limit),
        facecolor=chart_conf.bar_colour, edgecolor=chart_conf.line_colour)
    # ensure enough y-axis to show all of normpdf
    ymin, ymax = ax.get_ylim()
    norm_ys = get_normal_ys(vals, bins)
    logging.debug(norm_ys)
    logging.debug(f"ymin={ymin}, ymax={ymax}")
    logging.debug(f'norm max: {max(norm_ys)}; axis max: {ymax}')
    if max(norm_ys) > ymax:
        ax.set_ylim(ymax=1.05 * max(norm_ys))
    ## actually plot norm ys
    ax.plot(bins, norm_ys, color=chart_conf.line_colour, linewidth=4)
    logging.debug(f"n={n}, bins={bins}, patches={patches}")
    return fig

def get_scatterplot_fig(
        vars_series: Sequence[ScatterplotSeries],
        chart_conf: ScatterplotConf) -> Figure:
    fig, ax = plt.subplots()
    fig.set_size_inches((chart_conf.width_inches, chart_conf.height_inches))
    if chart_conf.xmin is not None and chart_conf.xmax is not None:
        ax.axis(xmin=chart_conf.xmin, xmax=chart_conf.xmax)
    if chart_conf.ymin is not None and chart_conf.ymax is not None:
        ax.axis(ymin=chart_conf.ymin, ymax=chart_conf.ymax)
    for var_series in vars_series:
        xs = []
        ys = []
        for coord in var_series.coords:
            xs.append(coord.x)
            ys.append(coord.y)
        dot_line_colour = (var_series.dot_line_colour if chart_conf.show_dot_lines
            else var_series.dot_colour)
        ax.plot(xs, ys, 'o', color=var_series.dot_colour, label=var_series.label,
            markeredgecolor=dot_line_colour)
        if var_series.show_regression_dets:
            ## Label can't be identical as the points series so add a space.
            ## Will look like correct and matching label without clashing.
            line_lbl = f"{var_series.label} " if var_series.label else ''
            regression_dets = get_regression_dets(xs, ys)
            ax.plot([min(xs), max(ys)], [regression_dets.y0, regression_dets.y1], '-',
                color=var_series.dot_colour, linewidth=5, label=line_lbl)
    return fig
