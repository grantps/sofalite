"""
Will point at GUI later but good for running functions in the meanwhile.
"""
from random import randint
from webbrowser import open_new_tab

import pandas as pd

from sofalite.conf.charts.output.non_standard import (
    BoxplotChartingSpec, BoxplotDataItem, BoxplotDataSeriesSpec, BoxplotIndivChartSpec,
    HistoChartingSpec, HistoIndivChartSpec,
    ScatterChartingSpec, ScatterDataSeriesSpec, ScatterIndivChartSpec)
from sofalite.conf.charts.output.standard import (
    AreaChartingSpec, BarChartingSpec, CategorySpec, DataItem, DataSeriesSpec,
    IndivChartSpec, LineChartingSpec, PieChartingSpec)
from sofalite.conf.misc import BoxplotType, SortOrder
from sofalite.conf.paths import DATABASE_FPATH
# noinspection PyUnresolvedReferences
from sofalite.output.charts import area, bar, boxplot, histo, line, pie, scatterplot  ## needed so singledispatch registration can occur
from sofalite.output.charts.common import get_html
from sofalite.output.styles.misc import get_style_spec
from sofalite.sql_extraction.charts import box_vals, freq_specs, histo_vals, xys
from sofalite.sql_extraction.db import Sqlite

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 500)

def run_clustered_bar_chart():
    style_dets = get_style_spec(style='default')
    category_specs = [
        CategorySpec(val=1, lbl='Ubuntu<br>Linux'),
        CategorySpec(val=2, lbl='Microsoft<br>Windows'),
        CategorySpec(val=3, lbl='Mac OSX'),
    ]
    series_data_items_male_nz = [
        DataItem(amount=125, lbl='125', tooltip='125'),
        DataItem(amount=40, lbl='40', tooltip='40'),
        DataItem(amount=50, lbl='50', tooltip='50'),
    ]
    series_data_items_male_aus = [
        DataItem(amount=725, lbl='725', tooltip='725'),
        DataItem(amount=210, lbl='210', tooltip='210'),
        DataItem(amount=200, lbl='200', tooltip='200'),
    ]
    data_series_spec_male_nz = DataSeriesSpec(
        lbl='NZ',
        data_items=series_data_items_male_nz,
    )
    data_series_spec_male_aus = DataSeriesSpec(
        lbl='Australia',
        data_items=series_data_items_male_aus,
    )
    indiv_chart_spec_male = IndivChartSpec(
        lbl='Male',
        data_series_specs=[data_series_spec_male_nz, data_series_spec_male_aus],
        n_records=1_024,
    )
    series_data_items_female_nz = [
        DataItem(amount=155, lbl='155', tooltip='155'),
        DataItem(amount=30, lbl='30', tooltip='30'),
        DataItem(amount=63, lbl='63', tooltip='63'),
    ]
    series_data_items_female_aus = [
        DataItem(amount=401, lbl='401', tooltip='401'),
        DataItem(amount=175, lbl='175', tooltip='175'),
        DataItem(amount=322, lbl='322', tooltip='322'),
    ]
    data_series_spec_female_nz = DataSeriesSpec(
        lbl='NZ',
        data_items=series_data_items_female_nz,
    )
    data_series_spec_female_aus = DataSeriesSpec(
        lbl='Australia',
        data_items=series_data_items_female_aus,
    )
    indiv_chart_spec_female = IndivChartSpec(
        lbl='Female',
        data_series_specs=[data_series_spec_female_nz, data_series_spec_female_aus],
        n_records=1_234,
    )
    charting_spec = BarChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec_male, indiv_chart_spec_female],
        legend_lbl='Country',
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title='Operating System',
        y_axis_title='Technical Excellence',
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_clustered_bar_chart.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_multi_line_chart():
    style_dets = get_style_spec(style='default')
    category_specs = [
        CategorySpec(val=1, lbl='Ubuntu<br>Linux'),
        CategorySpec(val=2, lbl='Microsoft<br>Windows'),
        CategorySpec(val=3, lbl='Mac OSX'),
    ]
    series_data_items_male_nz = [
        DataItem(amount=125, lbl='125', tooltip='125'),
        DataItem(amount=40, lbl='40', tooltip='40'),
        DataItem(amount=50, lbl='50', tooltip='50'),
    ]
    series_data_items_male_aus = [
        DataItem(amount=725, lbl='725', tooltip='725'),
        DataItem(amount=210, lbl='210', tooltip='210'),
        DataItem(amount=200, lbl='200', tooltip='200'),
    ]
    data_series_spec_male_nz = DataSeriesSpec(
        lbl='NZ',
        data_items=series_data_items_male_nz,
    )
    data_series_spec_male_aus = DataSeriesSpec(
        lbl='Australia',
        data_items=series_data_items_male_aus,
    )
    indiv_chart_spec_male = IndivChartSpec(
        lbl='Male',
        data_series_specs=[data_series_spec_male_nz, data_series_spec_male_aus],
        n_records=1_024,
    )
    series_data_items_female_nz = [
        DataItem(amount=155, lbl='155', tooltip='155'),
        DataItem(amount=30, lbl='30', tooltip='30'),
        DataItem(amount=63, lbl='63', tooltip='63'),
    ]
    series_data_items_female_aus = [
        DataItem(amount=401, lbl='401', tooltip='401'),
        DataItem(amount=175, lbl='175', tooltip='175'),
        DataItem(amount=322, lbl='322', tooltip='322'),
    ]
    data_series_spec_female_nz = DataSeriesSpec(
        lbl='NZ',
        data_items=series_data_items_female_nz,
    )
    data_series_spec_female_aus = DataSeriesSpec(
        lbl='Australia',
        data_items=series_data_items_female_aus,
    )
    indiv_chart_spec_female = IndivChartSpec(
        lbl='Female',
        data_series_specs=[data_series_spec_female_nz, data_series_spec_female_aus],
        n_records=1_234,
    )
    charting_spec = LineChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec_male, indiv_chart_spec_female],
        is_time_series=False,
        legend_lbl='Country',
        rotate_x_lbls=False,
        show_major_ticks_only=True,
        show_markers=True,
        show_smooth_line=False,
        show_trend_line=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title='Operating System',
        y_axis_title='Technical Excellence',
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_line_chart.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_area_chart():
    style_dets = get_style_spec(style='default')
    category_specs = [
        CategorySpec(val=1, lbl='Ubuntu<br>Linux'),
        CategorySpec(val=2, lbl='Microsoft<br>Windows'),
        CategorySpec(val=3, lbl='Mac OSX'),
        CategorySpec(val=4, lbl='BSD'),
    ]
    series_data_items_male = [
        DataItem(amount=125, lbl='125', tooltip='125'),
        DataItem(amount=40, lbl='40', tooltip='40'),
        DataItem(amount=50, lbl='50', tooltip='50'),
        DataItem(amount=12, lbl='12', tooltip='12'),
    ]
    data_series_spec_male = DataSeriesSpec(
        lbl=None,
        data_items=series_data_items_male,
    )
    indiv_chart_spec_male = IndivChartSpec(
        lbl='Male',
        data_series_specs=[data_series_spec_male, ],
        n_records=1_024,
    )
    series_data_items_female = [
        DataItem(amount=25, lbl='25', tooltip='25'),
        DataItem(amount=240, lbl='240', tooltip='240'),
        DataItem(amount=60, lbl='60', tooltip='60'),
        DataItem(amount=0, lbl='0', tooltip='0'),
    ]
    data_series_spec_female = DataSeriesSpec(
        lbl=None,
        data_items=series_data_items_female,
    )
    indiv_chart_spec_female = IndivChartSpec(
        lbl='Female',
        data_series_specs=[data_series_spec_female, ],
        n_records=1_233,
    )
    charting_spec = AreaChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec_male, indiv_chart_spec_female],
        is_time_series=False,
        legend_lbl='Country',
        rotate_x_lbls=False,
        show_major_ticks_only=False,
        show_markers=True,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title='Operating System',
        y_axis_title='Technical Excellence',
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_area_chart.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def get_random_data_items(*, n_amounts, min_range: int, max_range: int) -> list[DataItem]:
    data_items = []
    for i in range(n_amounts):
        amount = randint(min_range, max_range)
        boost = i / 1_000
        amount = round(amount * (1 + boost), 2)
        data_items.append(DataItem(amount=amount, lbl=str(amount), tooltip=str(amount)))
    return data_items

def run_time_series_chart_with_trend_and_smooth():
    style_dets = get_style_spec(style='default')
    category_specs = [
        CategorySpec(val='2022-01-01', lbl='2022-01-01'),
        CategorySpec(val='2022-02-01', lbl='2022-02-01'),
        CategorySpec(val='2022-03-01', lbl='2022-03-01'),
        CategorySpec(val='2022-04-01', lbl='2022-04-01'),
        CategorySpec(val='2022-05-01', lbl='2022-05-01'),
        CategorySpec(val='2022-06-01', lbl='2022-06-01'),
        CategorySpec(val='2022-07-01', lbl='2022-07-01'),
        CategorySpec(val='2022-08-01', lbl='2022-08-01'),
        CategorySpec(val='2022-09-01', lbl='2022-09-01'),
        CategorySpec(val='2022-10-01', lbl='2022-10-01'),
        CategorySpec(val='2022-11-01', lbl='2022-11-01'),
        CategorySpec(val='2022-12-01', lbl='2022-12-01'),
        CategorySpec(val='2023-01-01', lbl='2023-01-01'),
        CategorySpec(val='2023-02-01', lbl='2023-02-01'),
        CategorySpec(val='2023-03-01', lbl='2023-03-01'),
        CategorySpec(val='2023-04-01', lbl='2023-04-01'),
        CategorySpec(val='2023-05-01', lbl='2023-05-01'),
        CategorySpec(val='2023-06-01', lbl='2023-06-01'),
        CategorySpec(val='2023-07-01', lbl='2023-07-01'),
        CategorySpec(val='2023-08-01', lbl='2023-08-01'),
        CategorySpec(val='2023-09-01', lbl='2023-09-01'),
        CategorySpec(val='2023-10-01', lbl='2023-10-01'),
        CategorySpec(val='2023-11-01', lbl='2023-11-01'),
        CategorySpec(val='2023-12-01', lbl='2023-12-01'),
    ]
    series_data_items_male = get_random_data_items(n_amounts=len(category_specs), min_range=100, max_range=200)
    series_data_items_female = get_random_data_items(n_amounts=len(category_specs), min_range=50, max_range=250)
    data_series_spec_male = DataSeriesSpec(
        lbl='NZ',
        data_items=series_data_items_male,
    )
    data_series_spec_female = DataSeriesSpec(
        lbl='NZ',
        data_items=series_data_items_female,
    )
    indiv_chart_spec_male = IndivChartSpec(
        lbl='Male',
        data_series_specs=[data_series_spec_male, ],
        n_records=1_024,
    )
    indiv_chart_spec_female = IndivChartSpec(
        lbl='Female',
        data_series_specs=[data_series_spec_female, ],
        n_records=996,
    )
    charting_spec = LineChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec_male, indiv_chart_spec_female],
        is_time_series=True,
        legend_lbl='Country',
        rotate_x_lbls=False,
        show_major_ticks_only=True,
        show_markers=True,
        show_smooth_line=True,
        show_trend_line=True,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title='Operating System',
        y_axis_title='Extreme Technical Excellence',
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_time_series_chart_with_trend_and_smooth.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_pie_chart():
    style_dets = get_style_spec(style='default')
    ## https://en.wikipedia.org/wiki/List_of_operating_systems
    category_specs = [
        CategorySpec(val=1, lbl='Ubuntu<br>Linux'),
        CategorySpec(val=2, lbl='Microsoft<br>Windows'),
        CategorySpec(val=3, lbl='Mac OSX'),
        CategorySpec(val=4, lbl='AmigaOS'),
        CategorySpec(val=5, lbl='MINIX'),
        # CategorySpec(val=6, lbl='BSD'),  ## starts using DOJO colours because exhausts defined colours
    ]
    series_data_items_male = [
        DataItem(amount=125, lbl='125', tooltip='125'),
        DataItem(amount=40, lbl='40', tooltip='40'),
        DataItem(amount=50, lbl='50', tooltip='50'),
        DataItem(amount=13, lbl='13', tooltip='13'),
        DataItem(amount=15, lbl='15', tooltip='15'),
        # DataItem(amount=12, lbl='12', tooltip='12'),
    ]
    data_series_spec_male = DataSeriesSpec(
        lbl=None,
        data_items=series_data_items_male,
    )
    indiv_chart_spec_male = IndivChartSpec(
        lbl='Male',
        data_series_specs=[data_series_spec_male, ],
        n_records=1_024,
    )
    series_data_items_female = [
        DataItem(amount=25, lbl='25', tooltip='25'),
        DataItem(amount=49, lbl='49', tooltip='49'),
        DataItem(amount=150, lbl='150', tooltip='150'),
        DataItem(amount=0, lbl='0', tooltip='0'),
        DataItem(amount=15, lbl='15', tooltip='15'),
        # DataItem(amount=12, lbl='12', tooltip='12'),
    ]
    data_series_spec_female = DataSeriesSpec(
        lbl=None,
        data_items=series_data_items_female,
    )
    indiv_chart_spec_female = IndivChartSpec(
        lbl='Female',
        data_series_specs=[data_series_spec_female, ],
        n_records=1_195,
    )
    charting_spec = PieChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec_male, indiv_chart_spec_female],
        show_n_records=True,
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_pie_chart.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_histo():
    style_dets = get_style_spec(style='default')
    indiv_chart_spec_male = HistoIndivChartSpec(
        lbl='Male',
        n_records=1_312,
        norm_y_vals=[29.70628062839127, 40.091038388577154, 52.206878325617396, 65.59784034576569, 79.53032413643564,
            93.03735574497506, 105.01790732409468, 114.38017491702925, 120.2041738545691, 121.89046524097957,
            119.2617881350466, 112.59375254968397, 102.56723921258526, 90.15388223299749, 76.46128556756369,
            62.57201681216676, 49.408322163592004, 37.64449314484708, 27.67478127508274],
        y_vals=[98, 62, 88, 81, 88, 97, 103, 72, 78, 89, 70, 80, 69, 78, 83, 81, 89, 55, 39],
    )
    indiv_chart_spec_female = HistoIndivChartSpec(
        lbl='Female',
        n_records=1_453,
        norm_y_vals=[x * 0.6 for x in indiv_chart_spec_male.norm_y_vals],
        y_vals=[x * 0.6 for x in indiv_chart_spec_male.y_vals],
    )
    charting_spec = HistoChartingSpec(
        bin_lbls=[
            "1 to < 6.0",
            "6.0 to < 11.0",
            "11.0 to < 16.0",
            "16.0 to < 21.0",
            "21.0 to < 26.0",
            "26.0 to < 31.0",
            "31.0 to < 36.0",
            "36.0 to < 41.0",
            "41.0 to < 46.0",
            "46.0 to < 51.0",
            "51.0 to < 56.0",
            "56.0 to < 61.0",
            "61.0 to < 66.0",
            "66.0 to < 71.0",
            "71.0 to < 76.0",
            "76.0 to < 81.0",
            "81.0 to < 86.0",
            "86.0 to < 91.0",
            "91.0 to <= 96.0",
        ],
        indiv_chart_specs=[indiv_chart_spec_male, indiv_chart_spec_female],
        show_borders=True,
        show_n_records=True,
        show_normal_curve=True,
        var_lbl='Age',
        x_axis_font_size=10,
        x_axis_max_val=96,
        x_axis_min_val=1,
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_histo.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_scatterplot():
    style_dets = get_style_spec(style='default')
    data_series_spec_nz_male = ScatterDataSeriesSpec(
        lbl='Male',
        xy_pairs=[
            (7, 31.089077759478577),
            (8, 52.891415602937755),
            (9, 32.87885416438743),
            (10, 90.85113486779541),
            (11, 87.19061678974502),
            (11, 87.49566440860686),
            (11, 89.00882922272591),
            (11, 89.55456044434393),
            (11, 90.69881589314342),
            (12, 48.74874439217875),
            (12, 86.66766357627634),
            (13, 64.76123136158043),
            (13, 74.44631317552704),
            (13, 95.6063863541001),
            (14, 51.58931661038656),
            (14, 68.19186567513314),
            (14, 70.71394012931701),
            (14, 79.3761012964459),
            (14, 93.94852949416645),
            (15, 56.204624438512305),
            (15, 58.09672755327242),
            (15, 85.35586593517861),
            (15, 90.07135266618553),
            (16, 55.51422293022532),
            (16, 64.69980257279099),
            (16, 75.58194309176497),
            (16, 93.88227579864271),
            (17, 61.67143056102365),
            (17, 77.1608188576159),
            (18, 58.3639452016244),
            (18, 69.64475376710787),
            (18, 70.30809088041926),
            (19, 44.95230765247146),
            (19, 53.57549490141118),
            (19, 57.49166458987271),
            (19, 93.25999083552733),
            (19, 95.15021443541607),
            (20, 53.227022082249334),
            (20, 53.29474407886948),
            (20, 79.49675211721703),
            (20, 87.899776696556),
            (20, 102.06090563017703),
            (20, 103.59244502190629),
            (21, 52.710599562037316),
            (21, 71.1621463148663),
            (22, 58.65041170231558),
            (22, 63.22093774507396),
            (22, 76.5629751617783),
            (22, 93.56251928263522),
            (23, 55.401318241952325),
            (23, 63.96819568929662),
            (23, 81.64923062170921),
            (23, 82.38925947686283),
            (23, 97.90690497056967),
            (24, 56.65278954079034),
            (24, 87.25353952193792),
            (24, 102.77653328143441),
            (24, 104.24264378352584),
            (25, 62.63254251025136),
            (25, 75.78166771328051),
            (25, 85.96983017949809),
            (25, 88.53767338147256),
            (25, 94.1880058923127),
            (26, 67.39008556640098),
            (26, 101.33129699491217),
            (27, 59.4489078218154),
            (27, 73.32188403337558),
            (27, 94.49025627145032),
            (27, 105.3851256608892),
            (28, 63.66606754238583),
            (28, 81.2845387287078),
            (28, 88.79265107745631),
            (29, 65.91189105470143),
            (29, 69.7237603030059),
            (29, 86.88341340128035),
            (30, 53.45584988592154),
            (30, 75.0440371191352),
            (30, 75.66980434074233),
            (30, 78.63860548651503),
            (31, 86.24185065017261),
            (31, 103.47691222999252),
            (31, 110.8554531946424),
            (32, 72.03424626345567),
            (32, 100.26398794021729),
            (32, 100.89214107510836),
            (32, 103.64242134118042),
            (32, 106.8558340137951),
            (33, 54.38245239878321),
            (33, 70.2560026067812),
            (34, 54.552557369190495),
            (34, 58.29042842712961),
            (34, 58.29809783746975),
            (34, 70.58750492980703),
            (34, 70.83920486094253),
            (34, 79.08189084159216),
            (34, 88.25447469909444),
            (34, 99.8162865891165),
            (35, 55.74172261067245),
            (35, 55.97016338519753),
            (35, 88.49322934099736),
            (37, 70.76705034433678),
            (38, 82.85803998181666),
            (38, 84.9331415475707),
            (38, 85.5531033930658),
            (38, 109.27821440717126),
            (38, 109.54568217444003),
            (38, 112.9931152676548),
            (39, 50.87872942691264),
            (39, 68.42563412308716),
            (39, 83.47165181831294),
            (39, 90.94844247577886),
            (40, 55.95230971527245),
            (40, 93.55051885652135),
            (41, 70.47214973072266),
            (41, 79.43057687219917),
            (42, 66.92309413742817),
            (43, 62.10776017317396),
            (43, 65.23047276714242),
            (43, 107.09998735793931),
            (43, 114.69981585730503),
            (44, 61.49030874174853),
            (44, 72.7356644810264),
            (45, 85.78275742882836),
            (45, 86.40576376247002),
            (46, 64.34785830993653),
            (46, 66.88766954249277),
            (46, 67.7948803576885),
            (46, 102.41776316825892),
            (47, 95.15005267684302),
            (48, 55.63859214407223),
            (48, 81.26166953941211),
            (48, 84.51784665156677),
            (48, 91.80665689103873),
            (49, 60.32214610693401),
            (49, 62.402217261718356),
            (49, 103.35289937275952),
            (50, 88.54344910248898),
            (50, 112.14504411391337),
            (51, 60.36542147772364),
            (51, 97.51651807853864),
            (51, 117.0837243431976),
            (52, 72.39535438120788),
            (52, 112.70503652423116),
            (53, 59.01306155109371),
            (53, 86.03210127568012),
            (54, 88.88423903204715),
            (54, 97.44079675370708),
            (54, 98.50696113830162),
            (54, 121.27639806088153),
            (55, 71.98421611148714),
            (55, 112.91286394994879),
            (56, 73.30579481958063),
            (56, 73.68517507548506),
            (56, 124.53843530808524),
            (58, 89.3603561729845),
            (58, 98.16452427107139),
            (58, 99.9750209039127),
            (58, 112.61251531604402),
            (59, 81.70941351363436),
            (59, 111.87842429026593),
            (60, 62.88605727940337),
            (60, 67.6391022037282),
            (61, 61.81942257486523),
            (61, 111.29211999134988),
            (61, 126.504494397391),
            (62, 114.81220552536314),
            (62, 121.884480405658),
            (62, 129.62196505413857),
            (64, 64.085030581477),
            (65, 102.50088638835095),
            (66, 94.36855555470905),
            (67, 74.88094291416914),
            (68, 76.60026125640931),
            (68, 78.32012685299155),
            (68, 83.60718986814821),
            (68, 98.18385747521116),
            (70, 56.016112909164704),
            (70, 69.03097090451399),
            (70, 85.47047329887756),
            (70, 93.51419126566016),
            (70, 94.61475268830816),
            (70, 96.3201055380386),
            (70, 116.79562414429857),
            (70, 128.29474703696073),
            (70, 131.56019047008695),
            (71, 109.52631274679244),
            (72, 82.17453784142616),
            (72, 117.40970316602488),
            (73, 79.8854202039384),
            (73, 86.58092388817956),
            (73, 87.25880730561681),
            (73, 108.80472330057326),
            (74, 98.16864635669317),
            (75, 60.87719035366502),
            (75, 70.88388648073536),
            (75, 80.26217790323693),
            (75, 83.17153940685749),
            (75, 104.13287722480129),
            (76, 99.01955842814074),
            (77, 59.62952414145366),
            (77, 70.57169680474551),
            (78, 72.24024156184083),
            (78, 100.39337690632455),
            (78, 101.01086304617682),
            (78, 104.71550169136039),
            (79, 78.29429663365109),
            (79, 118.83477011797218),
            (80, 65.0882418854629),
            (81, 74.74665624550866),
            (82, 89.83910796250628),
            (82, 92.27181731999079),
            (82, 120.13325864815795),
            (82, 121.74666461316978),
            (82, 125.403795773468),
            (83, 77.0750427214925),
            (83, 81.94057422413667),
            (83, 84.48111602504024),
            (83, 103.87580849422537),
            (84, 64.13851748374992),
            (84, 79.10151077111617),
            (84, 105.13879158248183),
            (84, 105.72349466154242),
            (85, 57.849672122493644),
            (85, 107.18840345644851),
            (86, 63.78380732968341),
            (86, 99.57752311105126),
            (86, 105.0214821733067),
            (87, 108.00648097600289),
            (87, 111.83322217063261),
            (87, 119.68060267156304),
            (88, 53.88717239859486),
            (88, 79.1700679527727),
            (88, 94.67935712071801),
            (88, 98.26992367319721),
            (89, 77.72030596526385),
            (89, 81.2771983935041),
            (89, 112.96338280238284),
            (89, 126.05973280958811),
            (90, 58.770222469386205),
            (91, 98.10367164269518),
            (91, 119.15372639249875),
            (91, 121.08848591158159),
            (92, 73.27189323276932),
            (92, 112.34774201445076),
            (92, 117.50863435627296),
            (93, 74.56068933875537),
            (93, 79.46336199678751),
            (93, 98.93174515459495),
            (94, 93.63842512321644),
            (94, 96.52236774462664),
            (94, 106.52032779973688),
            (95, 73.40838458040419),
            (95, 74.14508112060757),
            (95, 108.14311977067007)
        ]
    )
    data_series_spec_nz_female = ScatterDataSeriesSpec(
        lbl='Female',
        xy_pairs=[
            (9, 29.770276469407097),
            (10, 75.02911151638259),
            (11, 46.690706901216984),
            (11, 78.00654390823837),
            (12, 42.5626720312458),
            (12, 74.15298785946761),
            (14, 37.63703674499805),
            (14, 68.27566980809932),
            (14, 80.33207766759574),
            (15, 49.1766467062098),
            (15, 81.44942235500378),
            (16, 42.70619731190737),
            (16, 56.12333910432752),
            (16, 57.85969989698726),
            (16, 60.20035301143594),
            (16, 64.43733326602266),
            (16, 76.01208103491183),
            (17, 80.76128823623553),
            (18, 44.423578382627355),
            (18, 60.74564622594354),
            (18, 63.13716117868855),
            (18, 76.88018469978608),
            (18, 78.06239633305547),
            (19, 60.986909470281155),
            (19, 71.18737116929105),
            (20, 58.59049708019984),
            (20, 67.79495528630112),
            (20, 80.33089052927403),
            (21, 60.24533643803302),
            (21, 80.99627269693173),
            (22, 44.04484382721852),
            (22, 52.23910336346455),
            (22, 74.45804926412096),
            (22, 81.04017961202295),
            (23, 40.10294433306821),
            (23, 55.89798237319415),
            (23, 80.58993568466052),
            (24, 39.930415120305184),
            (24, 43.537186235177714),
            (24, 80.37714905346178),
            (25, 41.6831177874809),
            (25, 73.1726827977343),
            (26, 39.7414332765329),
            (26, 48.30467519973595),
            (26, 52.085837554668046),
            (26, 61.522722957516045),
            (26, 79.77613655622663),
            (27, 41.72120112105925),
            (27, 75.1241054687545),
            (29, 41.75817861488493),
            (29, 52.49510995021312),
            (29, 54.47206521993609),
            (29, 75.50379406502566),
            (30, 66.07790632858871),
            (30, 85.7451851824555),
            (31, 80.66562328054265),
            (32, 45.150104873695504),
            (32, 63.49236814012789),
            (32, 78.85867093052025),
            (32, 83.50744641032271),
            (33, 54.11439182001775),
            (33, 67.10280728167618),
            (33, 73.79395909911005),
            (34, 62.45466673591653),
            (34, 64.07677213618808),
            (35, 77.14506217613796),
            (36, 47.73993715481558),
            (36, 58.81160497020908),
            (36, 81.5299081362206),
            (37, 45.77756961918132),
            (37, 49.774915185288826),
            (37, 78.90111418584993),
            (38, 55.26681483393362),
            (38, 73.80990158856697),
            (38, 75.48390853934522),
            (38, 76.00097229714854),
            (38, 82.96695739990481),
            (38, 87.11128258407412),
            (39, 57.07610412794405),
            (39, 73.25810103629914),
            (40, 50.740640732674564),
            (41, 56.723308049770495),
            (41, 60.86146555138049),
            (42, 46.035474938757616),
            (42, 46.805353786414976),
            (42, 49.137183928778136),
            (42, 53.471158513509614),
            (43, 74.55008901377981),
            (43, 80.3203058639792),
            (43, 80.63600288261468),
            (43, 92.15760036952969),
            (44, 44.32360060454546),
            (44, 94.06524062772031),
            (45, 70.71692809119844),
            (45, 76.55550169994474),
            (45, 85.42067545457115),
            (46, 50.66480936251611),
            (47, 45.848565598564434),
            (47, 76.55057841317615),
            (47, 80.17028477099228),
            (48, 46.86060078558708),
            (48, 48.09617223212737),
            (48, 54.29598144351387),
            (48, 81.22024572379975),
            (48, 88.77046987839958),
            (49, 61.03412596591154),
            (51, 85.4618098174859),
            (52, 47.91770778526955),
            (52, 63.81539260689578),
            (53, 57.190266042305936),
            (54, 68.71992550664096),
            (54, 72.45069411502705),
            (54, 99.50320750820211),
            (55, 61.13721039075928),
            (55, 63.324889323147005),
            (55, 67.61493511695916),
            (55, 81.37197337521145),
            (56, 66.39469107122349),
            (56, 74.06330645946927),
            (56, 83.76516265949563),
            (57, 47.382938849185564),
            (57, 75.19934224120054),
            (57, 95.18432712527296),
            (57, 97.61796895810552),
            (58, 51.953434216790974),
            (58, 52.32203670402945),
            (58, 60.120718719542786),
            (58, 70.44783600413851),
            (58, 85.71650217211781),
            (59, 74.0835567015066),
            (60, 57.05973925552533),
            (60, 70.7706733388255),
            (61, 50.857628252405846),
            (61, 93.45871199556336),
            (62, 78.12688322000538),
            (63, 90.81699482033474),
            (64, 85.0052916888199),
            (64, 89.42189186709676),
            (66, 64.36004757601306),
            (67, 51.33219949243679),
            (67, 51.34473710184353),
            (67, 63.60139544413424),
            (68, 42.42941538202076),
            (68, 86.45573328514901),
            (68, 97.69046110644888),
            (69, 50.99712044074546),
            (69, 62.859366896788565),
            (69, 85.83345391276045),
            (69, 106.06751699535718),
            (70, 54.4102505427813),
            (72, 50.36315224220876),
            (72, 52.90130682790542),
            (72, 67.71107924690172),
            (72, 87.60891810692532),
            (74, 89.07743530446291),
            (74, 94.52354856908735),
            (75, 73.61551621492585),
            (75, 73.96139413290618),
            (76, 60.56732623745026),
            (76, 67.04746446936059),
            (76, 83.7949730747118),
            (77, 71.9891054884759),
            (77, 81.98583988369958),
            (78, 54.34591184812273),
            (78, 68.46151037588463),
            (79, 66.64935226771395),
            (79, 79.4218151819556),
            (79, 80.16561909727125),
            (79, 81.99780264356956),
            (79, 90.40741105012414),
            (79, 103.2084557420431),
            (80, 90.81068773641182),
            (81, 67.38753454133773),
            (82, 53.39613339993172),
            (82, 54.70969853676342),
            (82, 63.51967452198149),
            (82, 68.42259750782057),
            (82, 75.22076928700659),
            (83, 71.5601110990537),
            (83, 82.96406792469526),
            (83, 86.20557976231719),
            (83, 91.0072264819529),
            (83, 97.80399691405584),
            (84, 52.23751430008849),
            (84, 60.73827192197558),
            (84, 101.73960304258202),
            (85, 60.12794439205489),
            (85, 72.13577307061455),
            (85, 96.81895667310681),
            (86, 47.32453675773932),
            (86, 86.527805911568),
            (88, 66.27720963628909),
            (88, 72.54185459394128),
            (89, 101.66687261438533),
            (90, 83.61472854353433),
            (91, 60.63837725604066),
            (92, 48.29088440501486),
            (92, 69.38413417154774),
            (92, 78.02582575275265),
            (92, 83.90869263344948),
            (92, 87.98656680204897),
            (92, 89.72483465365163),
            (93, 76.46744252085885),
            (94, 48.09186422487735),
            (94, 83.64965716765236),
            (95, 67.74827512824284),
            (95, 89.07095927006873),
            (95, 92.36272951096089),
            (96, 47.60992128696594),
            (96, 58.83869281988964),
            (96, 75.33963906724705)
        ]
    )
    indiv_chart_spec_nz = ScatterIndivChartSpec(
        data_series_specs=[data_series_spec_nz_male, data_series_spec_nz_female],
        lbl='NZ'
    )
    data_series_spec_aus_male = ScatterDataSeriesSpec(
        lbl='Male',
        xy_pairs=[
            (7, 31.089077759478577),
            (8, 52.891415602937755),
            (9, 32.87885416438743),
            (10, 90.85113486779541),
            (11, 87.19061678974502),
            (11, 87.49566440860686),
            (11, 89.00882922272591),
            (11, 89.55456044434393),
            (11, 90.69881589314342),
            (12, 48.74874439217875),
            (12, 86.66766357627634),
            (13, 64.76123136158043),
            (13, 74.44631317552704),
            (13, 95.6063863541001),
            (14, 51.58931661038656),
            (14, 68.19186567513314),
            (14, 70.71394012931701),
            (14, 79.3761012964459),
            (14, 93.94852949416645),
            (15, 56.204624438512305),
            (15, 58.09672755327242),
            (15, 85.35586593517861),
            (15, 90.07135266618553),
            (16, 55.51422293022532),
            (16, 64.69980257279099),
            (16, 75.58194309176497),
            (16, 93.88227579864271),
            (17, 61.67143056102365),
            (17, 77.1608188576159),
            (18, 58.3639452016244),
            (18, 69.64475376710787),
            (18, 70.30809088041926),
            (19, 44.95230765247146),
            (19, 53.57549490141118),
            (19, 57.49166458987271),
            (19, 93.25999083552733),
            (19, 95.15021443541607),
            (20, 53.227022082249334),
            (20, 53.29474407886948),
            (20, 79.49675211721703),
            (20, 87.899776696556),
            (20, 102.06090563017703),
            (20, 103.59244502190629),
            (21, 52.710599562037316),
            (21, 71.1621463148663),
            (22, 58.65041170231558),
            (22, 63.22093774507396),
            (22, 76.5629751617783),
            (22, 93.56251928263522),
            (23, 55.401318241952325),
            (23, 63.96819568929662),
            (23, 81.64923062170921),
            (23, 82.38925947686283),
            (23, 97.90690497056967),
            (24, 56.65278954079034),
            (24, 87.25353952193792),
            (24, 102.77653328143441),
            (24, 104.24264378352584),
            (25, 62.63254251025136),
            (25, 75.78166771328051),
            (25, 85.96983017949809),
            (25, 88.53767338147256),
            (25, 94.1880058923127),
            (26, 67.39008556640098),
            (26, 101.33129699491217),
            (27, 59.4489078218154),
            (27, 73.32188403337558),
            (27, 94.49025627145032),
            (27, 105.3851256608892),
            (28, 63.66606754238583),
            (28, 81.2845387287078),
            (28, 88.79265107745631),
            (29, 65.91189105470143),
            (29, 69.7237603030059),
            (29, 86.88341340128035),
            (30, 53.45584988592154),
            (30, 75.0440371191352),
            (30, 75.66980434074233),
            (30, 78.63860548651503),
            (31, 86.24185065017261),
            (31, 103.47691222999252),
            (31, 110.8554531946424),
            (32, 72.03424626345567),
            (32, 100.26398794021729),
            (32, 100.89214107510836),
            (32, 103.64242134118042),
            (32, 106.8558340137951),
            (33, 54.38245239878321),
            (33, 70.2560026067812),
            (34, 54.552557369190495),
            (34, 58.29042842712961),
            (34, 58.29809783746975),
            (34, 70.58750492980703),
            (34, 70.83920486094253),
            (34, 79.08189084159216),
            (34, 88.25447469909444),
            (34, 99.8162865891165),
            (35, 55.74172261067245),
            (35, 55.97016338519753),
            (35, 88.49322934099736),
            (37, 70.76705034433678),
            (38, 82.85803998181666),
            (38, 84.9331415475707),
            (38, 85.5531033930658),
            (38, 109.27821440717126),
            (38, 109.54568217444003),
            (38, 112.9931152676548),
            (39, 50.87872942691264),
            (39, 68.42563412308716),
            (39, 83.47165181831294),
            (39, 90.94844247577886),
            (40, 55.95230971527245),
            (40, 93.55051885652135),
            (41, 70.47214973072266),
            (41, 79.43057687219917),
            (42, 66.92309413742817),
            (43, 62.10776017317396),
            (43, 65.23047276714242),
            (43, 107.09998735793931),
            (43, 114.69981585730503),
            (44, 61.49030874174853),
            (44, 72.7356644810264),
            (45, 85.78275742882836),
            (45, 86.40576376247002),
            (46, 64.34785830993653),
            (46, 66.88766954249277),
            (46, 67.7948803576885),
            (46, 102.41776316825892),
            (47, 95.15005267684302),
            (48, 55.63859214407223),
            (48, 81.26166953941211),
            (48, 84.51784665156677),
            (48, 91.80665689103873),
            (49, 60.32214610693401),
            (49, 62.402217261718356),
            (49, 103.35289937275952),
            (50, 88.54344910248898),
            (50, 112.14504411391337),
            (51, 60.36542147772364),
            (51, 97.51651807853864),
            (51, 117.0837243431976),
            (52, 72.39535438120788),
            (52, 112.70503652423116),
            (53, 59.01306155109371),
            (53, 86.03210127568012),
            (54, 88.88423903204715),
            (54, 97.44079675370708),
            (54, 98.50696113830162),
            (54, 121.27639806088153),
            (55, 71.98421611148714),
            (55, 112.91286394994879),
            (56, 73.30579481958063),
            (56, 73.68517507548506),
            (56, 124.53843530808524),
            (58, 89.3603561729845),
            (58, 98.16452427107139),
            (58, 99.9750209039127),
            (58, 112.61251531604402),
            (59, 81.70941351363436),
            (59, 111.87842429026593),
            (60, 62.88605727940337),
            (60, 67.6391022037282),
            (61, 61.81942257486523),
            (61, 111.29211999134988),
            (61, 126.504494397391),
            (62, 114.81220552536314),
            (62, 121.884480405658),
            (62, 129.62196505413857),
            (64, 64.085030581477),
            (65, 102.50088638835095),
            (66, 94.36855555470905),
            (67, 74.88094291416914),
            (68, 76.60026125640931),
            (68, 78.32012685299155),
            (68, 83.60718986814821),
            (68, 98.18385747521116),
            (70, 56.016112909164704),
            (70, 69.03097090451399),
            (70, 85.47047329887756),
            (70, 93.51419126566016),
            (70, 94.61475268830816),
            (70, 96.3201055380386),
            (70, 116.79562414429857),
            (70, 128.29474703696073),
            (70, 131.56019047008695),
            (71, 109.52631274679244),
            (72, 82.17453784142616),
            (72, 117.40970316602488),
            (73, 79.8854202039384),
            (73, 86.58092388817956),
            (73, 87.25880730561681),
            (73, 108.80472330057326),
            (74, 98.16864635669317),
            (75, 60.87719035366502),
            (75, 70.88388648073536),
            (75, 80.26217790323693),
            (75, 83.17153940685749),
            (75, 104.13287722480129),
            (76, 99.01955842814074),
            (77, 59.62952414145366),
            (77, 70.57169680474551),
            (78, 72.24024156184083),
            (78, 100.39337690632455),
            (78, 101.01086304617682),
            (78, 104.71550169136039),
            (79, 78.29429663365109),
            (79, 118.83477011797218),
            (80, 65.0882418854629),
            (81, 74.74665624550866),
            (82, 89.83910796250628),
            (82, 92.27181731999079),
            (82, 120.13325864815795),
            (82, 121.74666461316978),
            (82, 125.403795773468),
            (83, 77.0750427214925),
            (83, 81.94057422413667),
            (83, 84.48111602504024),
            (83, 103.87580849422537),
            (84, 64.13851748374992),
            (84, 79.10151077111617),
            (84, 105.13879158248183),
            (84, 105.72349466154242),
            (85, 57.849672122493644),
            (85, 107.18840345644851),
            (86, 63.78380732968341),
            (86, 99.57752311105126),
            (86, 105.0214821733067),
            (87, 108.00648097600289),
            (87, 111.83322217063261),
            (87, 119.68060267156304),
            (88, 53.88717239859486),
            (88, 79.1700679527727),
            (88, 94.67935712071801),
            (88, 98.26992367319721),
            (89, 77.72030596526385),
            (89, 81.2771983935041),
            (89, 112.96338280238284),
            (89, 126.05973280958811),
            (90, 58.770222469386205),
            (91, 98.10367164269518),
            (91, 119.15372639249875),
            (91, 121.08848591158159),
            (92, 73.27189323276932),
            (92, 112.34774201445076),
            (92, 117.50863435627296),
            (93, 74.56068933875537),
            (93, 79.46336199678751),
            (93, 98.93174515459495),
            (94, 93.63842512321644),
            (94, 96.52236774462664),
            (94, 106.52032779973688),
            (95, 73.40838458040419),
            (95, 74.14508112060757),
            (95, 108.14311977067007)
        ]
    )
    data_series_spec_aus_female = ScatterDataSeriesSpec(
        lbl='Female',
        xy_pairs=[
            (9, 29.770276469407097),
            (10, 75.02911151638259),
            (11, 46.690706901216984),
            (11, 78.00654390823837),
            (12, 42.5626720312458),
            (12, 74.15298785946761),
            (14, 37.63703674499805),
            (14, 68.27566980809932),
            (14, 80.33207766759574),
            (15, 49.1766467062098),
            (15, 81.44942235500378),
            (16, 42.70619731190737),
            (16, 56.12333910432752),
            (16, 57.85969989698726),
            (16, 60.20035301143594),
            (16, 64.43733326602266),
            (16, 76.01208103491183),
            (17, 80.76128823623553),
            (18, 44.423578382627355),
            (18, 60.74564622594354),
            (18, 63.13716117868855),
            (18, 76.88018469978608),
            (18, 78.06239633305547),
            (19, 60.986909470281155),
            (19, 71.18737116929105),
            (20, 58.59049708019984),
            (20, 67.79495528630112),
            (20, 80.33089052927403),
            (21, 60.24533643803302),
            (21, 80.99627269693173),
            (22, 44.04484382721852),
            (22, 52.23910336346455),
            (22, 74.45804926412096),
            (22, 81.04017961202295),
            (23, 40.10294433306821),
            (23, 55.89798237319415),
            (23, 80.58993568466052),
            (24, 39.930415120305184),
            (24, 43.537186235177714),
            (24, 80.37714905346178),
            (25, 41.6831177874809),
            (25, 73.1726827977343),
            (26, 39.7414332765329),
            (26, 48.30467519973595),
            (26, 52.085837554668046),
            (26, 61.522722957516045),
            (26, 79.77613655622663),
            (27, 41.72120112105925),
            (27, 75.1241054687545),
            (29, 41.75817861488493),
            (29, 52.49510995021312),
            (29, 54.47206521993609),
            (29, 75.50379406502566),
            (30, 66.07790632858871),
            (30, 85.7451851824555),
            (31, 80.66562328054265),
            (32, 45.150104873695504),
            (32, 63.49236814012789),
            (32, 78.85867093052025),
            (32, 83.50744641032271),
            (33, 54.11439182001775),
            (33, 67.10280728167618),
            (33, 73.79395909911005),
            (34, 62.45466673591653),
            (34, 64.07677213618808),
            (35, 77.14506217613796),
            (36, 47.73993715481558),
            (36, 58.81160497020908),
            (36, 81.5299081362206),
            (37, 45.77756961918132),
            (37, 49.774915185288826),
            (37, 78.90111418584993),
            (38, 55.26681483393362),
            (38, 73.80990158856697),
            (38, 75.48390853934522),
            (38, 76.00097229714854),
            (38, 82.96695739990481),
            (38, 87.11128258407412),
            (39, 57.07610412794405),
            (39, 73.25810103629914),
            (40, 50.740640732674564),
            (41, 56.723308049770495),
            (41, 60.86146555138049),
            (42, 46.035474938757616),
            (42, 46.805353786414976),
            (42, 49.137183928778136),
            (42, 53.471158513509614),
            (43, 74.55008901377981),
            (43, 80.3203058639792),
            (43, 80.63600288261468),
            (43, 92.15760036952969),
            (44, 44.32360060454546),
            (44, 94.06524062772031),
            (45, 70.71692809119844),
            (45, 76.55550169994474),
            (45, 85.42067545457115),
            (46, 50.66480936251611),
            (47, 45.848565598564434),
            (47, 76.55057841317615),
            (47, 80.17028477099228),
            (48, 46.86060078558708),
            (48, 48.09617223212737),
            (48, 54.29598144351387),
            (48, 81.22024572379975),
            (48, 88.77046987839958),
            (49, 61.03412596591154),
            (51, 85.4618098174859),
            (52, 47.91770778526955),
            (52, 63.81539260689578),
            (53, 57.190266042305936),
            (54, 68.71992550664096),
            (54, 72.45069411502705),
            (54, 99.50320750820211),
            (55, 61.13721039075928),
            (55, 63.324889323147005),
            (55, 67.61493511695916),
            (55, 81.37197337521145),
            (56, 66.39469107122349),
            (56, 74.06330645946927),
            (56, 83.76516265949563),
            (57, 47.382938849185564),
            (57, 75.19934224120054),
            (57, 95.18432712527296),
            (57, 97.61796895810552),
            (58, 51.953434216790974),
            (58, 52.32203670402945),
            (58, 60.120718719542786),
            (58, 70.44783600413851),
            (58, 85.71650217211781),
            (59, 74.0835567015066),
            (60, 57.05973925552533),
            (60, 70.7706733388255),
            (61, 50.857628252405846),
            (61, 93.45871199556336),
            (62, 78.12688322000538),
            (63, 90.81699482033474),
            (64, 85.0052916888199),
            (64, 89.42189186709676),
            (66, 64.36004757601306),
            (67, 51.33219949243679),
            (67, 51.34473710184353),
            (67, 63.60139544413424),
            (68, 42.42941538202076),
            (68, 86.45573328514901),
            (68, 97.69046110644888),
            (69, 50.99712044074546),
            (69, 62.859366896788565),
            (69, 85.83345391276045),
            (69, 106.06751699535718),
            (70, 54.4102505427813),
            (72, 50.36315224220876),
            (72, 52.90130682790542),
            (72, 67.71107924690172),
            (72, 87.60891810692532),
            (74, 89.07743530446291),
            (74, 94.52354856908735),
            (75, 73.61551621492585),
            (75, 73.96139413290618),
            (76, 60.56732623745026),
            (76, 67.04746446936059),
            (76, 83.7949730747118),
            (77, 71.9891054884759),
            (77, 81.98583988369958),
            (78, 54.34591184812273),
            (78, 68.46151037588463),
            (79, 66.64935226771395),
            (79, 79.4218151819556),
            (79, 80.16561909727125),
            (79, 81.99780264356956),
            (79, 90.40741105012414),
            (79, 103.2084557420431),
            (80, 90.81068773641182),
            (81, 67.38753454133773),
            (82, 53.39613339993172),
            (82, 54.70969853676342),
            (82, 63.51967452198149),
            (82, 68.42259750782057),
            (82, 75.22076928700659),
            (83, 71.5601110990537),
            (83, 82.96406792469526),
            (83, 86.20557976231719),
            (83, 91.0072264819529),
            (83, 97.80399691405584),
            (84, 52.23751430008849),
            (84, 60.73827192197558),
            (84, 101.73960304258202),
            (85, 60.12794439205489),
            (85, 72.13577307061455),
            (85, 96.81895667310681),
            (86, 47.32453675773932),
            (86, 86.527805911568),
            (88, 66.27720963628909),
            (88, 72.54185459394128),
            (89, 101.66687261438533),
            (90, 83.61472854353433),
            (91, 60.63837725604066),
            (92, 48.29088440501486),
            (92, 69.38413417154774),
            (92, 78.02582575275265),
            (92, 83.90869263344948),
            (92, 87.98656680204897),
            (92, 89.72483465365163),
            (93, 76.46744252085885),
            (94, 48.09186422487735),
            (94, 83.64965716765236),
            (95, 67.74827512824284),
            (95, 89.07095927006873),
            (95, 92.36272951096089),
            (96, 47.60992128696594),
            (96, 58.83869281988964),
            (96, 75.33963906724705)
        ]
    )
    indiv_chart_spec_aus = ScatterIndivChartSpec(
        data_series_specs=[data_series_spec_aus_male, data_series_spec_aus_female],
        lbl='Australia'
    )
    charting_spec = ScatterChartingSpec(
        indiv_chart_specs=[indiv_chart_spec_nz, indiv_chart_spec_aus],
        legend_lbl='Gender',
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
        x_axis_title='Age',
        y_axis_title='Post-diet Weight',
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_scatterplot.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_boxplots():
    style_dets = get_style_spec(style='default')
    category_specs = [
        CategorySpec(val=1, lbl='New Zealand'),
        CategorySpec(val=2, lbl='United States'),
        CategorySpec(val=3, lbl='Canada'),
    ]
    box_item_male_nz = BoxplotDataItem(
        box_bottom=26,
        box_bottom_rounded=26,
        bottom_whisker=7,
        bottom_whisker_rounded=7,
        median=46,
        median_rounded=46,
        outliers=[],
        outliers_rounded=[],
        box_top=73,
        box_top_rounded=73,
        top_whisker=95,
        top_whisker_rounded=95,
    )
    box_item_male_us = BoxplotDataItem(
        box_bottom=17.5,
        box_bottom_rounded=17.5,
        bottom_whisker=1,
        bottom_whisker_rounded=1,
        median=43,
        median_rounded=43,
        outliers=[88, 88, 89],
        outliers_rounded=[88, 88, 89],
        box_top=66,
        box_top_rounded=66,
        top_whisker=86,
        top_whisker_rounded=86,
    )
    box_item_male_canada = BoxplotDataItem(
        box_bottom=26,
        box_bottom_rounded=26,
        bottom_whisker=1,
        bottom_whisker_rounded=1,
        median=43,
        median_rounded=43,
        outliers=[],
        outliers_rounded=[],
        box_top=68,
        box_top_rounded=68,
        top_whisker=91,
        top_whisker_rounded=91,
    )
    data_series_spec_male = BoxplotDataSeriesSpec(
        lbl='Male',
        box_items=[box_item_male_nz, box_item_male_us, box_item_male_canada],
    )
    box_item_female_nz = BoxplotDataItem(
        box_bottom=29,
        box_bottom_rounded=29,
        bottom_whisker=8,
        bottom_whisker_rounded=8,
        median=48.5,
        median_rounded=48.5,
        outliers=[],
        outliers_rounded=[],
        box_top=75.5,
        box_top_rounded=75.5,
        top_whisker=96,
        top_whisker_rounded=96,
    )
    box_item_female_canada = BoxplotDataItem(
        box_bottom=23,
        box_bottom_rounded=23,
        bottom_whisker=2,
        bottom_whisker_rounded=2,
        median=47,
        median_rounded=47,
        outliers=None,
        outliers_rounded=None,
        box_top=69,
        box_top_rounded=69,
        top_whisker=91,
        top_whisker_rounded=91,
    )
    data_series_spec_female = BoxplotDataSeriesSpec(
        lbl='Female',
        box_items=[box_item_female_nz, None, box_item_female_canada],  ## skipped one (US)
    )
    indiv_chart_spec = BoxplotIndivChartSpec(
        data_series_specs=[data_series_spec_male, data_series_spec_female],
        n_records=1_024,
    )
    charting_spec = BoxplotChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        legend_lbl='Gender',
        rotate_x_lbls=False,
        show_n_records=True,
        x_axis_title='Country',
        y_axis_title='Age',
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_boxplot.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def run_chart_data():
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        print(freq_specs.get_by_category_charting_spec(
            cur, tbl_name='demo_tbl',
            category_fld_name='gender', category_fld_lbl='Gender',
            category_vals2lbls={1: 'Male', 2: 'Female'},
            tbl_filt_clause=None))
        print(freq_specs.get_by_series_category_charting_spec(
            cur, tbl_name='demo_tbl',
            series_fld_name='browser', series_fld_lbl='Web Browser',
            category_fld_name='gender', category_fld_lbl='Gender',
            series_vals2lbls=None,
            category_vals2lbls={1: 'Male', 2: 'Female'},
            tbl_filt_clause=None))
        print(freq_specs.get_by_chart_series_category_charting_spec(
            cur, tbl_name='demo_tbl',
            chart_fld_name='country', chart_fld_lbl='Country',
            category_fld_name='gender', category_fld_lbl='Gender',
            chart_vals2lbls={1: 'Japan', 2: 'Italy', 3: 'Germany'},
            category_vals2lbls={1: 'Male', 2: 'Female'},
            tbl_filt_clause=None))
        print(freq_specs.get_by_chart_series_category_charting_spec(
            cur, tbl_name='demo_tbl',
            chart_fld_name='country', chart_fld_lbl='Country',
            series_fld_name='browser', series_fld_lbl='Web Browser',
            category_fld_name='gender', category_fld_lbl='Gender',
            chart_vals2lbls={1: 'Japan', 2: 'Italy', 3: 'Germany'},
            series_vals2lbls=None,
            category_vals2lbls={1: 'Male', 2: 'Female'},
            tbl_filt_clause=None))

def simple_bar_chart_from_data():
    ## conf
    style_dets = get_style_spec(style='grey_spirals')
    category_fld_name = 'gender'
    category_fld_lbl = 'Gender'
    category_vals2lbls = {1: 'Male', 2: 'Female'}
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_chart_category_charting_spec(
            cur, tbl_name='demo_tbl',
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None, category_sort_order=SortOrder.VALUE)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec()
    charting_spec = BarChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        legend_lbl=None,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_simple_bar_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_bar_chart_from_data():
    ## conf
    style_dets = get_style_spec(style='default')
    chart_fld_name = 'country'
    chart_fld_lbl = 'Country'
    category_fld_name = 'gender'
    category_fld_lbl = 'Gender'
    chart_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    category_vals2lbls = {1: 'Male', 2: 'Female'}
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_chart_category_charting_spec(
            cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None, category_sort_order=SortOrder.LABEL)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = BarChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=None,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_bar_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def clustered_bar_chart_from_data():
    ## conf
    style_dets = get_style_spec(style='default')
    series_fld_name = 'country'
    series_fld_lbl = 'Country'
    category_fld_name = 'gender'
    category_fld_lbl = 'Gender'
    series_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    category_vals2lbls = {1: 'Male', 2: 'Female'}
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_series_category_charting_spec(
            cur, tbl_name='demo_tbl',
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            series_vals2lbls=series_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None,
            category_sort_order=SortOrder.LABEL)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec()
    charting_spec = BarChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_clustered_bar_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_clustered_bar_chart_from_data():
    ## conf
    style_dets = get_style_spec(style='default')
    chart_fld_name = 'country'
    chart_fld_lbl = 'Country'
    series_fld_name = 'gender'
    series_fld_lbl = 'Gender'
    category_fld_name = 'browser'
    category_fld_lbl = 'Web Browser'
    chart_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    series_vals2lbls = {1: 'Male', 2: 'Female'}
    category_vals2lbls = {'Chrome': 'Google Chrome', }
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_chart_series_category_charting_spec(
            cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            series_vals2lbls=series_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause="(gender = 1 OR browser != 'Firefox')",
            category_sort_order=SortOrder.VALUE)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = BarChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_clustered_bar_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_line_chart_from_data():
    ## conf
    style_dets = get_style_spec(style='default')
    series_fld_name = 'country'
    series_fld_lbl = 'Country'
    category_fld_name = 'browser'
    category_fld_lbl = 'Web Browser'
    series_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    category_vals2lbls = {'Chrome': 'Google Chrome'}
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_series_category_charting_spec(
            cur, tbl_name='demo_tbl',
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            series_vals2lbls=series_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None,
            category_sort_order=SortOrder.LABEL)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec()
    charting_spec = LineChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec],
        is_time_series=False,
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        rotate_x_lbls=False,
        show_major_ticks_only=True,
        show_markers=True,
        show_smooth_line=False,
        show_trend_line=False,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_line_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def area_chart_from_data():
    ## conf
    style_dets = get_style_spec(style='default')
    chart_fld_name = 'country'
    chart_fld_lbl = 'Country'
    category_fld_name = 'browser'
    category_fld_lbl = 'Web Browser'
    chart_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    category_vals2lbls = {'Chrome': 'Google Chrome'}
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_chart_category_charting_spec(
            cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None,
            category_sort_order=SortOrder.LABEL)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = AreaChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=indiv_chart_specs,
        is_time_series=False,
        legend_lbl='Country',
        rotate_x_lbls=False,
        show_major_ticks_only=False,
        show_markers=True,
        show_n_records=True,
        x_axis_font_size=12,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title='Freq',
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_area_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def pie_chart_from_data():
    ## design
    style_dets = get_style_spec(style='default')
    chart_fld_name = 'country'
    chart_fld_lbl = 'Country'
    category_fld_name = 'browser'
    category_fld_lbl = 'Web Browser'
    chart_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    category_vals2lbls = {'Chrome': 'Google Chrome'}
    ## intermediate charting spec (including data)
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = freq_specs.get_by_chart_category_charting_spec(
            cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            tbl_filt_clause=None,
            category_sort_order=SortOrder.LABEL)
    ## charting spec
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = PieChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=indiv_chart_specs,
        show_n_records=True,
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_pie_chart_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def single_series_scatterplot_from_data():
    # ## conf
    style_dets = get_style_spec(style='default')
    x_fld_name = 'age'
    x_fld_lbl = 'Age'
    y_fld_name = 'weight'
    y_fld_lbl = 'Weight'
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = xys.get_by_series_xy_charting_spec(
            cur, tbl_name='demo_tbl',
            x_fld_name=x_fld_name, x_fld_lbl=x_fld_lbl,
            y_fld_name=y_fld_name, y_fld_lbl=y_fld_lbl,
            tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = ScatterChartingSpec(
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=None,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
        x_axis_title=intermediate_charting_spec.x_fld_lbl,
        y_axis_title=intermediate_charting_spec.y_fld_lbl,
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_single_series_scatterplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_series_scatterplot_from_data():
    # ## conf
    style_dets = get_style_spec(style='default')
    series_fld_name = 'gender'
    series_fld_lbl = 'Gender'
    series_vals2lbls = {1: 'Male', 2: 'Female'}
    x_fld_name = 'age'
    x_fld_lbl = 'Age'
    y_fld_name = 'weight'
    y_fld_lbl = 'Weight'
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = xys.get_by_series_xy_charting_spec(cur, tbl_name='demo_tbl',
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            x_fld_name=x_fld_name, x_fld_lbl=x_fld_lbl,
            y_fld_name=y_fld_name, y_fld_lbl=y_fld_lbl,
            series_vals2lbls=series_vals2lbls,
            tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = ScatterChartingSpec(
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
        x_axis_title=intermediate_charting_spec.x_fld_lbl,
        y_axis_title=intermediate_charting_spec.y_fld_lbl,
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_series_scatterplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_chart_scatterplot_from_data():
    ## conf
    style_dets = get_style_spec(style='default')
    chart_fld_name = 'gender'
    chart_fld_lbl = 'Gender'
    chart_vals2lbls = {1: 'Male', 2: 'Female'}
    x_fld_name = 'age'
    x_fld_lbl = 'Age'
    y_fld_name = 'weight'
    y_fld_lbl = 'Weight'
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = xys.get_by_chart_xy_charting_spec(cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            x_fld_name=x_fld_name, x_fld_lbl=x_fld_lbl,
            y_fld_name=y_fld_name, y_fld_lbl=y_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = ScatterChartingSpec(
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=None,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
        x_axis_title=intermediate_charting_spec.x_fld_lbl,
        y_axis_title=intermediate_charting_spec.y_fld_lbl,
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_chart_scatterplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_chart_series_scatterplot_from_data():
    ## conf
    style_dets = get_style_spec(style='default')
    chart_fld_name = 'gender'
    chart_fld_lbl = 'Gender'
    chart_vals2lbls = {1: 'Male', 2: 'Female'}
    series_fld_name = 'country'
    series_fld_lbl = 'Country'
    series_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    x_fld_name = 'age'
    x_fld_lbl = 'Age'
    y_fld_name = 'weight'
    y_fld_lbl = 'Weight'
    ## data details
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = xys.get_by_chart_series_xy_charting_spec(cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            x_fld_name=x_fld_name, x_fld_lbl=x_fld_lbl,
            y_fld_name=y_fld_name, y_fld_lbl=y_fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            series_vals2lbls=series_vals2lbls,
            tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    charting_spec = ScatterChartingSpec(
        indiv_chart_specs=indiv_chart_specs,
        legend_lbl=series_fld_lbl,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
        x_axis_title=intermediate_charting_spec.x_fld_lbl,
        y_axis_title=intermediate_charting_spec.y_fld_lbl,
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_chart_series_scatterplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def histogram_from_data():
    ## conf
    dp = 3
    style_dets = get_style_spec(style='default')
    fld_name = 'age'
    fld_lbl = 'Age'
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = histo_vals.get_by_vals_charting_spec(
            cur, tbl_name='demo_tbl', fld_name=fld_name, fld_lbl=fld_lbl, tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    bin_lbls = intermediate_charting_spec.to_bin_lbls(dp=dp)
    x_axis_min_val, x_axis_max_val = intermediate_charting_spec.to_x_axis_range()
    charting_spec = HistoChartingSpec(
        bin_lbls=bin_lbls,
        indiv_chart_specs=indiv_chart_specs,
        show_borders=False,
        show_n_records=True,
        show_normal_curve=True,
        var_lbl=intermediate_charting_spec.fld_lbl,
        x_axis_font_size=12,
        x_axis_max_val=x_axis_max_val,
        x_axis_min_val=x_axis_min_val,
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_histogram_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_chart_histogram_from_data():
    ## conf
    dp = 3
    style_dets = get_style_spec(style='default')
    chart_fld_name = 'gender'
    chart_fld_lbl = 'Gender'
    chart_vals2lbls = {1: 'Male', 2: 'Female'}
    fld_name = 'age'
    fld_lbl = 'Age'
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = histo_vals.get_by_chart_charting_spec(cur, tbl_name='demo_tbl',
            chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
            fld_name=fld_name, fld_lbl=fld_lbl,
            chart_vals2lbls=chart_vals2lbls,
            tbl_filt_clause=None)
    ## charts details
    indiv_chart_specs = intermediate_charting_spec.to_indiv_chart_specs()
    bin_lbls = intermediate_charting_spec.to_bin_lbls(dp=dp)
    x_axis_min_val, x_axis_max_val = intermediate_charting_spec.to_x_axis_range()
    charting_spec = HistoChartingSpec(
        bin_lbls=bin_lbls,
        indiv_chart_specs=indiv_chart_specs,
        show_borders=False,
        show_n_records=True,
        show_normal_curve=True,
        var_lbl=intermediate_charting_spec.fld_lbl,
        x_axis_font_size=12,
        x_axis_max_val=x_axis_max_val,
        x_axis_min_val=x_axis_min_val,
    )
    ## output
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_multi_chart_histogram_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def boxplot_from_data():
    ## conf
    dp = 3
    style_dets = get_style_spec(style='default')
    category_fld_name = 'country'
    category_fld_lbl = 'Country'
    category_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    fld_name = 'age'
    fld_lbl = 'Age'
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = box_vals.get_by_series_category_charting_spec(cur, tbl_name='demo_tbl',
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            fld_name=fld_name, fld_lbl=fld_lbl,
            tbl_filt_clause=None,
            category_vals2lbls=category_vals2lbls,
            category_sort_order=SortOrder.VALUE,
            boxplot_type=BoxplotType.IQR_1_PT_5_OR_INSIDE)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec(dp=dp)
    charting_spec = BoxplotChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        rotate_x_lbls=False,
        show_n_records=True,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title=intermediate_charting_spec.fld_lbl,
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_boxplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

def multi_series_boxplot_from_data():
    ## conf
    dp = 3
    style_dets = get_style_spec(style='default')
    series_fld_name = 'gender'
    series_fld_lbl = 'Gender'
    series_vals2lbls = {1: 'Male', 2: 'Female'}
    category_fld_name = 'country'
    category_fld_lbl = 'Country'
    category_vals2lbls = {1: 'Japan', 2: 'Italy', 3: 'Germany'}
    fld_name = 'age'
    fld_lbl = 'Age'
    with Sqlite(DATABASE_FPATH) as (_con, cur):
        intermediate_charting_spec = box_vals.get_by_series_category_charting_spec(cur, tbl_name='demo_tbl',
            series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
            category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
            fld_name=fld_name, fld_lbl=fld_lbl,
            tbl_filt_clause=None,
            series_vals2lbls=series_vals2lbls,
            category_vals2lbls=category_vals2lbls,
            category_sort_order=SortOrder.VALUE,
            boxplot_type=BoxplotType.IQR_1_PT_5_OR_INSIDE)
    ## charts details
    category_specs = intermediate_charting_spec.to_sorted_category_specs()
    indiv_chart_spec = intermediate_charting_spec.to_indiv_chart_spec(dp=dp)
    charting_spec = BoxplotChartingSpec(
        category_specs=category_specs,
        indiv_chart_specs=[indiv_chart_spec, ],
        legend_lbl=intermediate_charting_spec.series_fld_lbl,
        rotate_x_lbls=False,
        show_n_records=True,
        x_axis_title=intermediate_charting_spec.category_fld_lbl,
        y_axis_title=intermediate_charting_spec.fld_lbl,
    )
    html = get_html(charting_spec, style_dets)
    fpath = '/home/g/Documents/sofalite/reports/test_multiseries_boxplot_from_data.html'
    with open(fpath, 'w') as f:
        f.write(html)
    open_new_tab(url=f"file://{fpath}")

# simple_bar_chart_from_data()
# multi_bar_chart_from_data()
# clustered_bar_chart_from_data()
# multi_clustered_bar_chart_from_data()
# multi_line_chart_from_data()
# area_chart_from_data()
# pie_chart_from_data()
# single_series_scatterplot_from_data()
# multi_series_scatterplot_from_data()
# multi_chart_scatterplot_from_data()
# multi_chart_series_scatterplot_from_data()
# histogram_from_data()
# multi_chart_histogram_from_data()
# boxplot_from_data()
# multi_series_boxplot_from_data()

# run_chart_data()
#
# run_clustered_bar_chart()
# run_multi_line_chart()
# run_time_series_chart_with_trend_and_smooth()
# run_area_chart()
# run_pie_chart()
# run_histo()
# run_scatterplot()
# run_boxplots()
