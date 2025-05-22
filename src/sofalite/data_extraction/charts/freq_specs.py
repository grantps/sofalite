"""
These functions are not responsible for sort order of category values (by value, by label etc).
Nor are they responsible for having placeholders for empty items
e.g. one country series lacks a certain web browser value
It is the dataclasses returned by these functions that are responsible for empty values.
Empty values are handled in their methods responsible for translating into charts specs
e.g. to_indiv_chart_spec().

Sort order always includes by value and by label. Only single chart, single series charts
also sort by increasing and decreasing.

The job of these functions is to get all the details you could possibly want about the data -
including labels, amounts etc. - into a dataclass.

These dataclasses should have everything included that directly relates to the data - field labels, value labels etc.
They shouldn't contain any settings which are purely about style or display.

For example:
IN: chart_lbl
OUT: rotate_x_lbls, show_n_records, legend_lbl (as such - might actually be one of the data labels)
"""
import pandas as pd

from collections.abc import Sequence
from dataclasses import dataclass
from textwrap import dedent

from sofalite.data_extraction.db import ExtendedCursor
from sofalite.data_extraction.interfaces import CategorySpec, DataItem, DataSeriesSpec, IndivChartSpec
from sofalite.stats_calc.interfaces import SortOrder

## by category only (one chart, one series)

@dataclass(frozen=True)
class CategoryItemFreqSpec:
    """
    Frequency-related specification for an individual category value e.g. for Japan
    Frequency-related includes percentage. Both freq and pct are about the number of items.
    """
    category_val: float | str  ## e.g. 1
    category_val_lbl: str  ## e.g. Japan
    freq: int
    category_pct: float

@dataclass(frozen=True)
class CategoryFreqSpecs:
    """
    Store frequency and percentage for each category value e.g. Japan in a category variable e.g. country

    Category-by variable label e.g. country, and one spec related to frequency per country value
    e.g. one for Italy, one for Germany etc.
    Frequency-related includes percentage. Both freq and pct are about the number of items.
    """
    category_fld_lbl: str  ## e.g. Country
    category_freq_specs: Sequence[CategoryItemFreqSpec]  ## e.g. one freq spec per country
    category_sort_order: SortOrder

    def __str__(self):
        bits = [f"Category field value: {self.category_fld_lbl}", ]
        for freq_spec in self.category_freq_specs:
            bits.append(f"    {freq_spec}")
        return dedent('\n'.join(bits))

    def to_sorted_category_specs(self) -> Sequence[CategorySpec]:
        """
        Get category specs in correct order ready for use.
        The category specs are constant across all charts and series (if multi-chart and / or multi-series)

        Only makes sense to order by INCREASING or DECREASING if single series and single chart.
        """
        if self.category_sort_order == SortOrder.VALUE:
            def sort_me(freq_spec):
                return freq_spec.category_val
            reverse = False
        elif self.category_sort_order == SortOrder.LABEL:
            def sort_me(freq_spec):
                return freq_spec.category_val_lbl
            reverse = False
        elif self.category_sort_order == SortOrder.INCREASING:
            def sort_me(freq_spec):
                return freq_spec.freq
            reverse = False
        elif self.category_sort_order == SortOrder.DECREASING:
            def sort_me(freq_spec):
                return freq_spec.freq
            reverse = True
        else:
            raise Exception(f"Unexpected category_sort_order ({self.category_sort_order})")
        all_category_freq_specs = self.category_freq_specs
        category_specs = [
            CategorySpec(freq_spec.category_val, freq_spec.category_val_lbl)
            for freq_spec in sorted(all_category_freq_specs, key=sort_me, reverse=reverse)
        ]
        return category_specs

    def to_indiv_chart_spec(self) -> IndivChartSpec:
        n_records = sum(category_freq_spec.freq for category_freq_spec in self.category_freq_specs)
        category_specs = self.to_sorted_category_specs()
        ## collect data items according to correctly sorted x-axis category items
        ## a) make dict so we can get from val to data item
        vals2data_items = {}
        for category_freq_spec in self.category_freq_specs:
            val = category_freq_spec.category_val
            data_item = DataItem(
                amount=category_freq_spec.freq,
                lbl=str(category_freq_spec.freq),
                tooltip=f"{category_freq_spec.freq}<br>({round(category_freq_spec.category_pct, 2)}%)")
            vals2data_items[val] = data_item
        ## b) create sorted collection of data items according to x-axis sorting.
        ## Note - never gaps for by-category only charts
        series_data_items = []
        for category_spec in category_specs:
            val = category_spec.val
            data_item = vals2data_items.get(val)
            series_data_items.append(data_item)
        ## assemble
        data_series_spec = DataSeriesSpec(
            lbl=None,
            data_items=series_data_items,
        )
        indiv_chart_spec = IndivChartSpec(
            lbl=None,
            data_series_specs=[data_series_spec, ],
            n_records=n_records,
        )
        return indiv_chart_spec

## by category and by series

@dataclass(frozen=True)
class SeriesCategoryFreqSpec:
    """
    Frequency-related specifications for each category value within this particular value of the series-by variable.
    Frequency-related includes percentage. Both freq and pct are about the number of items.
    """
    series_val: float | str  ## e.g. 1
    series_val_lbl: str  ## e.g. Male
    category_freq_specs: Sequence[CategoryItemFreqSpec]  ## one frequency-related spec per country

    def __str__(self):
        bits = [f"Series value (label): {self.series_val} ({self.series_val_lbl})", ]
        for freq_spec in self.category_freq_specs:
            bits.append(f"        {freq_spec}")
        return dedent('\n'.join(bits))

def _to_sorted_category_specs_for_multi_series_chart_case(self) -> Sequence[CategorySpec]:
    """
    Get category specs in correct order ready for use.
    The category specs are constant across all series (and charts).
    This code is shared across all cases where we have multiple series and / or charts
    i.e. sorting by frequencies doesn't really make sense.
    So we only expect by value or by label ordering.
    """
    if self.category_sort_order == SortOrder.VALUE:
        def sort_me(freq_spec):
            return freq_spec.category_val
        reverse = False
    elif self.category_sort_order == SortOrder.LABEL:
        def sort_me(freq_spec):
            return freq_spec.category_val_lbl
        reverse = False
    else:
        raise Exception(
            f"Unexpected category_sort_order ({self.category_sort_order})"
            "\nINCREASING and DECREASING not allowed when multi-series charts."
        )
    all_category_freq_specs = self._get_all_category_freq_specs()
    category_specs = [
        CategorySpec(freq_spec.category_val, freq_spec.category_val_lbl)
        for freq_spec in sorted(all_category_freq_specs, key=sort_me, reverse=reverse)
    ]
    return category_specs

@dataclass(frozen=True)
class SeriesCategoryFreqSpecs:
    """
    Against each series store frequency and percentage for each category value
    e.g. Japan in a category variable e.g. country
    Also store labels for series and category as a convenience so all the building blocks are in one place.

    Series-by variable label e.g. Gender, and category-by variable label e.g. country,
    and one spec related to frequency per country value
    e.g. one for Italy, one for Germany etc.
    Frequency-related includes percentage. Both freq and pct are about the number of items.
    """
    series_fld_lbl: str  ## e.g. Gender
    category_fld_lbl: str  ## e.g. Country
    series_category_freq_specs: Sequence[SeriesCategoryFreqSpec]
    category_sort_order: SortOrder

    def __str__(self):
        bits = [
            f"Series field label: {self.series_fld_lbl}",
            f"Category field label: {self.category_fld_lbl}",
        ]
        for series_category_freq_spec in self.series_category_freq_specs:
            bits.append(f"    {series_category_freq_spec}")
        return dedent('\n'.join(bits))

    def _get_all_category_freq_specs(self) -> Sequence[CategoryItemFreqSpec]:
        all_category_freq_specs = []
        vals = set()
        for series_category_freq_spec in self.series_category_freq_specs:
            for freq_spec in series_category_freq_spec.category_freq_specs:
                if freq_spec.category_val not in vals:
                    all_category_freq_specs.append(freq_spec)
                    vals.add(freq_spec.category_val)
        return list(all_category_freq_specs)

    def to_sorted_category_specs(self) -> Sequence[CategorySpec]:
        return _to_sorted_category_specs_for_multi_series_chart_case(self)

    def to_indiv_chart_spec(self) -> IndivChartSpec:
        n_records = 0
        category_specs = self.to_sorted_category_specs()
        data_series_specs = []
        for series_category_freq_spec in self.series_category_freq_specs:
            ## prepare for sorting category items within this series (may even have missing items)
            vals2data_items = {}
            for freq_spec in series_category_freq_spec.category_freq_specs:
                ## count up n_records while we're here in loop
                n_records += freq_spec.freq
                ## collect data items according to correctly sorted x-axis category items
                ## a) make dict so we can get from val to data item
                val = freq_spec.category_val
                tooltip = (f"{freq_spec.category_val_lbl}, {series_category_freq_spec.series_val_lbl}"
                   f"<br>{freq_spec.freq}"
                   f"<br>({round(freq_spec.category_pct, 2)}%)")
                data_item = DataItem(
                    amount=freq_spec.freq,
                    lbl=str(freq_spec.freq),
                    tooltip=tooltip)
                vals2data_items[val] = data_item
            ## b) create sorted collection of data items according to x-axis sorting.
            ## Note - gaps should become None (which .get() automatically handles for us :-))
            series_data_items = []
            for category_spec in category_specs:
                val = category_spec.val
                data_item = vals2data_items.get(val)
                series_data_items.append(data_item)
            data_series_spec = DataSeriesSpec(
                lbl=series_category_freq_spec.series_val_lbl,
                data_items=series_data_items,
            )
            data_series_specs.append(data_series_spec)
        indiv_chart_spec = IndivChartSpec(
            lbl=None,
            data_series_specs=data_series_specs,
            n_records=n_records,
        )
        return indiv_chart_spec

## multi-chart, one series each chart by category

@dataclass(frozen=True)
class ChartCategoryFreqSpec:
    """
    Frequency-related specifications for each category value within this particular value of the chart-by variable.
    Frequency-related includes percentage. Both freq and pct are about the number of items.
    """
    chart_val: float | str
    chart_val_lbl: str
    category_freq_specs: Sequence[CategoryItemFreqSpec]

    def __str__(self):
        bits = [f"Chart value (label): {self.chart_val} ({self.chart_val_lbl})", ]
        for freq_spec in self.category_freq_specs:
            bits.append(f"        {freq_spec}")
        return dedent('\n'.join(bits))

@dataclass(frozen=True)
class ChartCategoryFreqSpecs:
    """
    Against each chart store frequency and percentage for each category value
    e.g. Japan in a category variable e.g. country
    Also store labels for chart and category as a convenience so all the building blocks are in one place.
    """
    chart_fld_lbl: str  ## e.g. Web Browser
    category_fld_lbl: str  ## e.g. Country
    chart_category_freq_specs: Sequence[ChartCategoryFreqSpec]
    category_sort_order: SortOrder

    def __str__(self):
        bits = [
            f"Chart field label: {self.chart_fld_lbl}",
            f"Category field label: {self.category_fld_lbl}",
        ]
        for chart_category_freq_spec in self.chart_category_freq_specs:
            bits.append(f"    {chart_category_freq_spec}")
        return dedent('\n'.join(bits))

    def _get_all_category_freq_specs(self) -> Sequence[CategoryItemFreqSpec]:
        all_category_freq_specs = []
        vals = set()
        for chart_category_freq_spec in self.chart_category_freq_specs:
            for freq_spec in chart_category_freq_spec.category_freq_specs:
                if freq_spec.category_val not in vals:
                    all_category_freq_specs.append(freq_spec)
                    vals.add(freq_spec.category_val)
        return list(all_category_freq_specs)

    def to_sorted_category_specs(self) -> Sequence[CategorySpec]:
        return _to_sorted_category_specs_for_multi_series_chart_case(self)

    def to_indiv_chart_specs(self) -> Sequence[IndivChartSpec]:
        indiv_chart_specs = []
        n_records = 0
        category_specs = self.to_sorted_category_specs()
        for chart_category_freq_spec in self.chart_category_freq_specs:
            ## prepare for sorting category items within this chart (may even have missing items)
            vals2data_items = {}
            for freq_spec in chart_category_freq_spec.category_freq_specs:
                ## count up n_records while we're here in loop
                n_records += freq_spec.freq
                ## collect data items according to correctly sorted x-axis category items
                ## a) make dict so we can get from val to data item
                val = freq_spec.category_val
                tooltip = f"{freq_spec.freq}<br>({round(freq_spec.category_pct, 2)}%)"
                data_item = DataItem(
                    amount=freq_spec.freq,
                    lbl=str(freq_spec.freq),
                    tooltip=tooltip)
                vals2data_items[val] = data_item
            ## b) create sorted collection of data items according to x-axis sorting.
            ## Note - gaps should become None (which .get() automatically handles for us :-))
            chart_data_items = []
            for category_spec in category_specs:
                val = category_spec.val
                data_item = vals2data_items.get(val)
                chart_data_items.append(data_item)
            data_series_spec = DataSeriesSpec(
                lbl=None,
                data_items=chart_data_items,
            )
            indiv_chart_spec = IndivChartSpec(
                lbl=f"{self.chart_fld_lbl}: {chart_category_freq_spec.chart_val_lbl}",
                data_series_specs=[data_series_spec, ],
                n_records=n_records,
            )
            indiv_chart_specs.append(indiv_chart_spec)
        return indiv_chart_specs

## Chart, series, category

@dataclass(frozen=True)
class ChartSeriesCategoryFreqSpec:
    """
    Nested within each value of the chart-by variable, within each value of the series-by variable,
    collect frequency-related specifications for each category value.
    Frequency-related includes percentage. Both freq and pct are about the number of items.
    """
    chart_val: float | str
    chart_val_lbl: str
    series_category_freq_specs: Sequence[SeriesCategoryFreqSpec]

    def __str__(self):
        bits = [f"Chart value (label): {self.chart_val} ({self.chart_val_lbl})", ]
        for series_category_freq_spec in self.series_category_freq_specs:
            bits.append(f"    {series_category_freq_spec}")
        return dedent('\n'.join(bits))

@dataclass(frozen=True)
class ChartSeriesCategoryFreqSpecs:
    """
    Against each chart and series store frequency and percentage for each category value
    e.g. Japan in a category variable e.g. country
    Also store labels for chart, series, and category as a convenience so all the building blocks are in one place.
    """
    chart_fld_lbl: str  ## e.g. Web Browser
    series_fld_lbl: str  ## e.g. Gender
    category_fld_lbl: str  ## e.g. Country
    chart_series_category_freq_specs: Sequence[ChartSeriesCategoryFreqSpec]
    category_sort_order: SortOrder

    def __str__(self):
        bits = [
            f"Chart field label: {self.chart_fld_lbl}",
            f"Series field label: {self.series_fld_lbl}",
            f"Category field label: {self.category_fld_lbl}",
        ]
        for chart_series_category_freq_spec in self.chart_series_category_freq_specs:
            bits.append(f"{chart_series_category_freq_spec}")
        return dedent('\n'.join(bits))

    def _get_all_category_freq_specs(self) -> Sequence[CategoryItemFreqSpec]:
        all_category_freq_specs = []
        vals = set()
        for chart_series_category_freq_spec in self.chart_series_category_freq_specs:
            for series_category_freq_specs in chart_series_category_freq_spec.series_category_freq_specs:
                for freq_spec in series_category_freq_specs.category_freq_specs:
                    if freq_spec.category_val not in vals:
                        all_category_freq_specs.append(freq_spec)
                        vals.add(freq_spec.category_val)
        return list(all_category_freq_specs)

    def to_sorted_category_specs(self) -> Sequence[CategorySpec]:
        return _to_sorted_category_specs_for_multi_series_chart_case(self)

    def to_indiv_chart_specs(self) -> Sequence[IndivChartSpec]:
        indiv_chart_specs = []
        category_specs = self.to_sorted_category_specs()
        for chart_series_category_freq_spec in self.chart_series_category_freq_specs:
            n_records = 0
            data_series_specs = []
            for series_category_freq_spec in chart_series_category_freq_spec.series_category_freq_specs:
                ## prepare for sorting category items within this chart (may even have missing items)
                vals2data_items = {}
                for freq_spec in series_category_freq_spec.category_freq_specs:
                    ## count up n_records while we're here in loop
                    n_records += freq_spec.freq
                    ## collect data items according to correctly sorted x-axis category items
                    ## a) make dict so we can get from val to data item
                    val = freq_spec.category_val
                    tooltip = (
                        f"{freq_spec.category_val_lbl}, {series_category_freq_spec.series_val_lbl}"
                        f"<br>{freq_spec.freq}"
                        f"<br>({round(freq_spec.category_pct, 2)}%)")
                    data_item = DataItem(
                        amount=freq_spec.freq,
                        lbl=str(freq_spec.freq),
                        tooltip=tooltip)
                    vals2data_items[val] = data_item
                ## b) create sorted collection of data items according to x-axis sorting.
                ## Note - gaps should become None (which .get() automatically handles for us :-))
                chart_series_data_items = []
                for category_spec in category_specs:
                    val = category_spec.val
                    data_item = vals2data_items.get(val)
                    chart_series_data_items.append(data_item)
                data_series_spec = DataSeriesSpec(
                    lbl=series_category_freq_spec.series_val_lbl,
                    data_items=chart_series_data_items,
                )
                data_series_specs.append(data_series_spec)
            indiv_chart_spec = IndivChartSpec(
                lbl=f"{self.chart_fld_lbl}: {chart_series_category_freq_spec.chart_val_lbl}",
                data_series_specs=data_series_specs,
                n_records=n_records,
            )
            indiv_chart_specs.append(indiv_chart_spec)
        return indiv_chart_specs

def get_by_category_charting_spec(cur: ExtendedCursor, src_tbl_name: str,
        category_fld_name: str, category_fld_lbl: str, category_vals2lbls: dict | None = None,
        category_sort_order: SortOrder = SortOrder.VALUE, tbl_filt_clause: str | None = None) -> CategoryFreqSpecs:
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{category_fld_name}` AS
      category_val,
        COUNT(*) AS
      freq,
        (100.0 * COUNT(*)) / (SELECT COUNT(*) FROM `{src_tbl_name}`) AS
      raw_category_pct
    FROM {src_tbl_name}
    WHERE `{category_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY `{category_fld_name}`
    ORDER BY `{category_fld_name}`
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    ## build result
    category_freq_specs = []
    for category_val, freq, category_pct in data:
        freq_spec = CategoryItemFreqSpec(
            category_val=category_val, category_val_lbl=category_vals2lbls.get(category_val, str(category_val)),
            freq=int(freq), category_pct=category_pct)
        category_freq_specs.append(freq_spec)
    data_spec = CategoryFreqSpecs(
        category_fld_lbl=category_fld_lbl,
        category_freq_specs=category_freq_specs,
        category_sort_order=category_sort_order,
    )
    return data_spec

def get_by_series_category_charting_spec(cur: ExtendedCursor, src_tbl_name: str,
        series_fld_name: str, series_fld_lbl: str,
        category_fld_name: str, category_fld_lbl: str,
        series_vals2lbls: dict | None,
        category_vals2lbls: dict | None,
        category_sort_order: SortOrder = SortOrder.VALUE,
        tbl_filt_clause: str | None = None) -> SeriesCategoryFreqSpecs:
    series_vals2lbls = {} if series_vals2lbls is None else series_vals2lbls
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{series_fld_name}` AS
      series_val,
        `{category_fld_name}` AS
      category_val,
        COUNT(*) AS
      freq,
        ((100.0 * COUNT(*))
        / (
          SELECT COUNT(*)
          FROM `{src_tbl_name}`
          WHERE `{series_fld_name}` = src.{series_fld_name}
        )) AS
      raw_category_pct
    FROM {src_tbl_name} AS src
    WHERE `{series_fld_name}` IS NOT NULL
    AND `{category_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY `{series_fld_name}`, `{category_fld_name}`
    ORDER BY `{series_fld_name}`, `{category_fld_name}`
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    cols = ['series_val', 'category_val', 'freq', 'raw_category_pct']
    df = pd.DataFrame(data, columns=cols)
    series_category_freq_specs = []
    for series_val in df['series_val'].unique():
        category_item_freq_specs = []
        for _i, (category_val, freq, raw_category_pct) in df.loc[
            df['series_val'] == series_val,
            ['category_val', 'freq', 'raw_category_pct']
        ].iterrows():
            freq_spec = CategoryItemFreqSpec(
                category_val=category_val,
                category_val_lbl=category_vals2lbls.get(category_val, category_val),
                freq=int(freq),
                category_pct=raw_category_pct,
            )
            category_item_freq_specs.append(freq_spec)
        series_category_freq_spec = SeriesCategoryFreqSpec(
            series_val=series_val,
            series_val_lbl=series_vals2lbls.get(series_val, series_val),
            category_freq_specs=category_item_freq_specs,
        )
        series_category_freq_specs.append(series_category_freq_spec)
    data_spec = SeriesCategoryFreqSpecs(
        series_fld_lbl=series_fld_lbl,
        category_fld_lbl=category_fld_lbl,
        series_category_freq_specs=series_category_freq_specs,
        category_sort_order=category_sort_order,
    )
    return data_spec

def get_by_chart_category_charting_spec(cur: ExtendedCursor, src_tbl_name: str,
        chart_fld_name: str, chart_fld_lbl: str,
        category_fld_name: str, category_fld_lbl: str,
        chart_vals2lbls: dict | None,
        category_vals2lbls: dict | None,
        category_sort_order: SortOrder = SortOrder.VALUE,
        tbl_filt_clause: str | None = None) -> ChartCategoryFreqSpecs:
    chart_vals2lbls = {} if chart_vals2lbls is None else chart_vals2lbls
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{chart_fld_name}` AS
      chart_val,
        `{category_fld_name}` AS
      category_val,
        COUNT(*) AS
      freq,
        ((100.0 * COUNT(*))
        / (
          SELECT COUNT(*)
          FROM `{src_tbl_name}`
          WHERE `{chart_fld_name}` = src.{chart_fld_name}
        )) AS
      raw_category_pct
    FROM {src_tbl_name} AS src
    WHERE `{chart_fld_name}` IS NOT NULL
    AND `{category_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY `{chart_fld_name}`, `{category_fld_name}`
    ORDER BY `{chart_fld_name}`, `{category_fld_name}`
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    cols = ['chart_val', 'category_val', 'freq', 'raw_category_pct']
    df = pd.DataFrame(data, columns=cols)
    chart_category_freq_specs = []
    for chart_val in df['chart_val'].unique():
        freq_specs = []
        for _i, (category_val, freq, raw_category_pct) in df.loc[
                    df['chart_val'] == chart_val,
                    ['category_val', 'freq', 'raw_category_pct']
                ].iterrows():
            freq_spec = CategoryItemFreqSpec(
                category_val=category_val,
                category_val_lbl=category_vals2lbls.get(category_val, category_val),
                freq=int(freq),
                category_pct=raw_category_pct,
            )
            freq_specs.append(freq_spec)
        chart_category_freq_spec = ChartCategoryFreqSpec(
            chart_val=chart_val,
            chart_val_lbl=chart_vals2lbls.get(chart_val, chart_val),
            category_freq_specs=freq_specs,
        )
        chart_category_freq_specs.append(chart_category_freq_spec)
    charting_spec = ChartCategoryFreqSpecs(
        chart_fld_lbl=chart_fld_lbl,
        category_fld_lbl=category_fld_lbl,
        chart_category_freq_specs=chart_category_freq_specs,
        category_sort_order=category_sort_order,
    )
    return charting_spec

def get_by_chart_series_category_charting_spec(cur: ExtendedCursor, src_tbl_name: str,
         chart_fld_name: str, chart_fld_lbl: str,
         series_fld_name: str, series_fld_lbl: str,
         category_fld_name: str, category_fld_lbl: str,
         chart_vals2lbls: dict | None,
         series_vals2lbls: dict | None,
         category_vals2lbls: dict | None,
         category_sort_order: SortOrder = SortOrder.VALUE,
         tbl_filt_clause: str | None = None) -> ChartSeriesCategoryFreqSpecs:
    chart_vals2lbls = {} if chart_vals2lbls is None else chart_vals2lbls
    series_vals2lbls = {} if series_vals2lbls is None else series_vals2lbls
    category_vals2lbls = {} if category_vals2lbls is None else category_vals2lbls
    ## prepare clauses
    and_tbl_filt_clause = f"AND ({tbl_filt_clause})" if tbl_filt_clause else ''
    ## assemble SQL
    sql = f"""\
    SELECT
        `{chart_fld_name}` AS
      chart_val,
        `{series_fld_name}` AS
      series_val,
        `{category_fld_name}` AS
      category_val,
        COUNT(*) AS
      freq,
        ((100.0 * COUNT(*))
        / (
          SELECT COUNT(*)
          FROM `{src_tbl_name}`
          WHERE `{chart_fld_name}` = src.{chart_fld_name}
          AND `{series_fld_name}` = src.{series_fld_name}
        )) AS
      raw_category_pct
    FROM {src_tbl_name} AS src
    WHERE `{chart_fld_name}` IS NOT NULL
    AND `{series_fld_name}` IS NOT NULL
    AND `{category_fld_name}` IS NOT NULL
    {and_tbl_filt_clause}
    GROUP BY `{chart_fld_name}`, `{series_fld_name}`, `{category_fld_name}`
    ORDER BY `{chart_fld_name}`, `{series_fld_name}`, `{category_fld_name}`
    """
    ## get data
    cur.exe(sql)
    data = cur.fetchall()
    cols = ['chart_val', 'series_val', 'category_val', 'freq', 'raw_category_pct']
    df = pd.DataFrame(data, columns=cols)
    chart_series_category_freq_specs = []
    for chart_val in df['chart_val'].unique():
        series_category_freq_specs = []
        for series_val in df.loc[df['chart_val'] == chart_val, 'series_val'].unique():
            freq_specs = []
            for _i, (category_val, freq, raw_category_pct) in df.loc[
                (df['chart_val'] == chart_val) & (df['series_val'] == series_val),
                ['category_val', 'freq', 'raw_category_pct']
            ].iterrows():
                freq_spec = CategoryItemFreqSpec(
                    category_val=category_val,
                    category_val_lbl=category_vals2lbls.get(category_val, category_val),
                    freq=int(freq),
                    category_pct=raw_category_pct,
                )
                freq_specs.append(freq_spec)
            series_category_freq_spec = SeriesCategoryFreqSpec(
                series_val=series_val,
                series_val_lbl=series_vals2lbls.get(series_val, series_val),
                category_freq_specs=freq_specs,
            )
            series_category_freq_specs.append(series_category_freq_spec)
        chart_series_category_freq_spec = ChartSeriesCategoryFreqSpec(
            chart_val=chart_val,
            chart_val_lbl=chart_vals2lbls.get(chart_val, str(chart_val)),
            series_category_freq_specs=series_category_freq_specs,
        )
        chart_series_category_freq_specs.append(chart_series_category_freq_spec)
    data_spec = ChartSeriesCategoryFreqSpecs(
        chart_fld_lbl=chart_fld_lbl,
        series_fld_lbl=series_fld_lbl,
        category_fld_lbl=category_fld_lbl,
        chart_series_category_freq_specs=chart_series_category_freq_specs,
        category_sort_order=category_sort_order,
    )
    return data_spec

def get_freq_specs(cur: ExtendedCursor, src_tbl_name: str,
        category_fld_name: str, category_fld_lbl: str,
        chart_fld_name: str | None = None, chart_fld_lbl: str | None = None,
        series_fld_name: str | None = None, series_fld_lbl: str | None = None,
        chart_vals2lbls: dict | None = None,
        series_vals2lbls: dict | None = None,
        category_vals2lbls: dict | None = None,
        tbl_filt_clause: str | None = None) -> ChartSeriesCategoryFreqSpecs:
    """
    Single interface irrespective of which settings are None
    e.g. if no By Chart variable selected can still use same interface.
    Convenient when calling code from a GUI.
    """
    if chart_fld_name is None:  ## no chart
        if series_fld_name is None:  ## no series (so category only)
            data_spec = get_by_category_charting_spec(
                cur=cur, src_tbl_name=src_tbl_name,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
        else:  ## series and category
            data_spec = get_by_series_category_charting_spec(
                cur=cur, src_tbl_name=src_tbl_name,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
                series_vals2lbls=series_vals2lbls,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
    else:  ## chart
        if series_fld_name is None:  ## chart and category only (no series)
            data_spec = get_by_chart_category_charting_spec(
                cur=cur, src_tbl_name=src_tbl_name,
                chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                chart_vals2lbls=chart_vals2lbls,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
        else:  ## chart, series, and category
            data_spec = get_by_chart_series_category_charting_spec(
                cur=cur, src_tbl_name=src_tbl_name,
                chart_fld_name=chart_fld_name, chart_fld_lbl=chart_fld_lbl,
                series_fld_name=series_fld_name, series_fld_lbl=series_fld_lbl,
                category_fld_name=category_fld_name, category_fld_lbl=category_fld_lbl,
                chart_vals2lbls=chart_vals2lbls,
                series_vals2lbls=series_vals2lbls,
                category_vals2lbls=category_vals2lbls,
                tbl_filt_clause=tbl_filt_clause)
    return data_spec
