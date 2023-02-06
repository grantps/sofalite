import logging
import math
from typing import Sequence

from sofalite.conf.misc import BinWidthDets, HistogramDetails, NiceInitialBinDets

def get_nice_initial_bin_details(*, min_val, max_val, n_distinct) -> NiceInitialBinDets:
    """
    Goal - set nice bin widths so 'nice' value e.g. 0.2, 0.5, 1 (or
    200, 500, 1000 or 0.002, 0.005, 0.01) and not too many or too few bins.

    Start with a bin width which splits the data into the optimal number of
    bins. Normalise it, adjust upwards to nice size, and denormalise. Check
    number of bins resulting.

    OK? If room to double number of bins, halve size of normalised bin width,
    and try to adjust upwards to a nice size. This time, however, there is the
    option of 2 as an interval size (so we have 2, 5, or 10. Denormalise and
    recalculate the number of bins.

    Now reset lower and upper limits if appropriate. Make lower limit a multiple
    of the bin_width and make upper limit n_bins*bin_width higher.

    Add another bin if not covering max value.

    n_bins -- need an integer ready for core_stats.histogram
    """
    ## init
    if min_val > max_val:
        logging.debug(f'Had to swap {min_val} and {max_val} ...')
        min_val, max_val = max_val, min_val
        logging.debug(f'... to {min_val} and {max_val}')
    data_range = max_val - min_val
    if data_range == 0:
        data_range = 1
    target_n_bins = 20
    """
    If lots of values then 10, otherwise n_distinct unless too low in which case
    4 at lowest.
    """
    if n_distinct >= 10:
        min_n_bins = 10
    elif n_distinct <= 4:
        min_n_bins = 4
    else:
        min_n_bins = n_distinct
    init_bin_width = data_range / (target_n_bins * 1.0)
    ## normalise init_bin_width to val between 1 and 10
    norm_bin_width = init_bin_width
    while norm_bin_width <= 1:
        norm_bin_width *= 10
    while norm_bin_width > 10:
        norm_bin_width /= 10.0
    logging.debug(f'init_bin_width={init_bin_width}, '
        f'norm_bin_width={norm_bin_width}')
    ## get denorm ratio so can convert norm_bin widths back to data bin widths
    denorm_ratio = init_bin_width/norm_bin_width
    ## adjust upwards to either 5 or 10
    better_norm_bin_width = 5 if norm_bin_width <= 5 else 10
    ## denormalise
    better_bin_width = better_norm_bin_width*denorm_ratio
    n_bins = int(math.ceil(data_range / better_bin_width))
    ## possible to increase granularity?
    if n_bins < min_n_bins:
        ## halve normalised bin width and try again but with an extra option of 2
        norm_bin_width /= 2.0
        if norm_bin_width <= 2:
            better_norm_bin_width = 2
        elif norm_bin_width <= 5:
            better_norm_bin_width = 5
        else:
            better_norm_bin_width = 10
        ## denormalise
        better_bin_width = better_norm_bin_width*denorm_ratio
        n_bins = int(math.ceil(data_range / (better_bin_width * 1.0)))
    lower_limit = min_val
    upper_limit = max_val
    ## Adjust lower and upper limits if bin_width doesn't exactly fit.
    ## If an exact fit, leave alone on assumption the limits are meaningful
    ## e.g. if 9.69 - 19.69 and 20 bins then leave limits alone.
    if better_bin_width * n_bins != data_range:
        logging.debug(f"data_range={data_range}, "
            f"better_bin_width*n_bins={better_bin_width * n_bins}")
        ## Set lower limit to a clean multiple of the bin_width
        ## e.g. 3*bin_width or -6*bin_width.
        ## Identify existing multiple and set to integer below (floor).
        ## Lower limit is now that lower integer times the bin_width.
        ## NB the multiple is an integer but the lower limit might not be
        ## e.g. if the bin_size is a fraction e.g. 0.002
        existing_multiple = lower_limit/(better_bin_width*1.0)
        lower_limit = math.floor(existing_multiple) * better_bin_width
        upper_limit = lower_limit + (n_bins * better_bin_width)
    if max_val > upper_limit:
        upper_limit += better_bin_width
        n_bins += 1
    logging.debug(f'For {min_val} to {max_val} use an interval size of '
        f'{better_bin_width} for a data range of '
        f'{lower_limit} to {upper_limit} giving you {n_bins} bins')
    return NiceInitialBinDets(n_bins, lower_limit, upper_limit)

def _get_limits_and_bin_width(vals: Sequence[float],
        n_bins=10, limits: tuple[float, float] | None = None) -> BinWidthDets:
    if limits is None:  ## no limits given for histogram, both must be calculated
        est_bin_width = (max(vals) - min(vals)) / float(n_bins) + 1e-6  ## 1=>cover all
        bin_width = (max(vals) - min(vals) + est_bin_width) / float(n_bins)
        lower_real_limit = min(vals) - bin_width / 2  ## lower real limit, 1st bin
        upper_real_limit = 1.000001 * max(vals)  ## added so able to include top val in final bin. Use same code as orig to calc upp from lower
    else:
        lower_real_limit, upper_real_limit = limits
        bin_width = (upper_real_limit - lower_real_limit) / float(n_bins)
    return BinWidthDets(bin_width, lower_real_limit, upper_real_limit)

def get_histogram_details(vals: Sequence[float], n_bins=10, limits=None,
        inc_uppermost_val_in_top_bin=True) -> HistogramDetails:
    """
    Includes the uppermost value in top bin.
    This is essential if wanting to have "nice", human-readable bins e.g. 10 to < 20
    because the only alternatives are worse.
    NB label of top bin must be explicit about including upper values.
    Known problem with continuous distributions.

    Returns:
    (i) a list of histogram bin counts
    (ii) the smallest value of the histogram binning
    (iii) the bin width
    (the last 2 are not necessarily integers).
    Default number of bins is 10.
    If no sequence object is given for default_real_limits,
    the routine picks (usually non-pretty) bins spanning all the numbers in bin_freqs.
    """
    bin_dets = _get_limits_and_bin_width(vals, n_bins=n_bins, limits=limits)
    bin_freqs = [0] * n_bins
    n_extra_points = 0
    for val in vals:
        try:
            if (val - bin_dets.lower_limit) < 0 and inc_uppermost_val_in_top_bin:
                n_extra_points += 1
            else:
                if val == bin_dets.upper_limit:  ## includes uppermost value in top bin
                    bin_freqs[n_bins - 1] += 1
                else:  ## the original always did this if not (num - lower_real_limit) < 0
                    bin2increment = int((val - bin_dets.lower_limit) / float(bin_dets.bin_width))
                    bin_freqs[bin2increment] = bin_freqs[bin2increment] + 1
        except Exception:
            n_extra_points += 1
    return HistogramDetails(bin_freqs, bin_dets.lower_limit, bin_dets.bin_width, n_extra_points)

def has_saw_toothing(bin_freqs: Sequence[float], period: int, start_idx: int = 0) -> bool:
    """
    Saw-toothing is where every nth bin has values, but the others have none.
    """
    period_vals = bin_freqs[start_idx::period]
    sum_period = sum(period_vals)
    sum_all = sum(bin_freqs)
    sum_non_period = sum_all - sum_period
    return sum_non_period == 0

def fix_saw_toothing(
        vals: Sequence[float], initial_n_bins: int, limits: tuple[float, float],  ## enough to recalculate histogram details
        orig_histogram_details: HistogramDetails  ## existing details to be updated
        ) -> HistogramDetails:
    """
    Look for saw-toothing on commonly found periods (5 and 2).
    If found, reduce bins until problem gone or too few bins to keep shrinking.

    Assuming we have enough bins to permit shrinking,
    we try to get acceptable histogram details.
    If they're not OK, we feed them back in, so we have the inputs we need to apply a further shrink factor.
    """
    fixed_histogram_details = orig_histogram_details  ## we might have 5 or fewer bins in which case we skip out
    n_bins = initial_n_bins
    while n_bins > 5:
        bin_freqs = fixed_histogram_details.bins_freqs  ## as the number of bins shrinks these change (same or upwards)
        if has_saw_toothing(bin_freqs, period=5):
            shrink_factor = 5.0
        elif has_saw_toothing(bin_freqs, period=2):
            shrink_factor = 2.0
        elif has_saw_toothing(bin_freqs, period=2, start_idx=1):
            shrink_factor = 2.0
        else:
            break
        ## all we are changing is the number of bins (reducing them) and then getting fresh results
        n_bins = int(math.ceil(n_bins / shrink_factor))
        fixed_histogram_details = get_histogram_details(vals, n_bins, limits)
        logging.debug(fixed_histogram_details)
    return fixed_histogram_details

_vals = [1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,3,3,3,3,3,3,4,4,4,5,5,5,6,6,6,6,12,13,13,13,20,20,34,34,34,35,36,45,45,77]
print(_vals)
print(get_histogram_details(_vals, n_bins=4))
