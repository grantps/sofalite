from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Sequence

from sofalite.conf.charts.output.standard import CategorySpec, DataItem, DataSeriesSpec, IndivChartSpec
from sofalite.conf.misc import SortOrder

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
