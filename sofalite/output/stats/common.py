import base64
from io import BytesIO
from typing import Sequence

from sofalite.conf.style import ChartStyleDets
from sofalite.output.charts import mpl_pngs
from sofalite.output.charts.conf import HistogramConf, HistogramData

def get_group_histogram_html(measure_fld_lbl: str, style_dets: ChartStyleDets,
        var_lbl: str, vals: Sequence[float]) -> str:
    """
    Make histogram image and return its HTML (with embedded image).
    """
    first_colour_mapping = style_dets.colour_mappings[0]
    chart_conf = HistogramConf(
        var_lbl=var_lbl,
        chart_lbl=measure_fld_lbl,
        inner_bg_colour=style_dets.plot_bg_colour,
        bar_colour=first_colour_mapping.main,
        line_colour=style_dets.major_grid_line_colour)
    data_dets = HistogramData(vals)
    fig = mpl_pngs.get_histogram_fig(chart_conf, data_dets)
    fig.set_size_inches((5.0, 3.5))  ## see dpi to get image size in pixels
    bio = BytesIO()
    fig.savefig(bio)
    chart_base64 = base64.b64encode(bio.getvalue()).decode('utf-8')
    html = f'<img src="data:image/png;base64,{chart_base64}"/>'
    return html
