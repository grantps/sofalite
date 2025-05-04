from collections.abc import Sequence
import base64
from io import BytesIO

from sofalite.output.charts import mpl_pngs
from sofalite.output.charts.histogram import HistogramConf
from sofalite.output.styles.interfaces import ChartStyleSpec

def get_group_histogram_html(measure_fld_lbl: str, style_spec: ChartStyleSpec,
        var_lbl: str, vals: Sequence[float]) -> str:
    """
    Make histogram image and return its HTML (with embedded image).
    """
    first_colour_mapping = style_spec.colour_mappings[0]
    chart_conf = HistogramConf(
        var_lbl=var_lbl,
        chart_lbl=measure_fld_lbl,
        inner_bg_colour=style_spec.plot_bg_colour,
        bar_colour=first_colour_mapping.main,
        line_colour=style_spec.major_grid_line_colour)
    fig = mpl_pngs.get_histogram_fig(chart_conf, vals)
    fig.set_size_inches((5.0, 3.5))  ## see dpi to get image size in pixels
    bio = BytesIO()
    fig.savefig(bio)
    chart_base64 = base64.b64encode(bio.getvalue()).decode('utf-8')
    html = f'<img src="data:image/png;base64,{chart_base64}"/>'
    return html
