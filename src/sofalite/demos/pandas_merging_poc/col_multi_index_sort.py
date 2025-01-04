from enum import StrEnum
from functools import cache, partial
from itertools import count
import sqlite3 as sqlite
from typing import Any

import pandas as pd

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 500)

class Sort(StrEnum):
    LBL = 'by label'
    VAL = 'by value'
    INCREASING = 'by increasing freq'
    DECREASING = 'by decreasing freq'

class Metric(StrEnum):
    FREQ = 'freq'
    ROW_PCT = 'row pct'
    COL_PCT = 'col pct'

BLANK = '__blank__'

class SortUtils:

    @staticmethod
    @cache
    def get_raw_df(*, debug=False) -> pd.DataFrame:
        con = sqlite.connect('sofa_db')
        cur = con.cursor()
        sql = """\
        SELECT id, agegroup as age, browser, car
        FROM demo_tbl
        """
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        con.close()
        df = pd.DataFrame(data, columns=['id', 'age', 'browser', 'car', ])
        df['browser'] = df['browser'].apply(lambda s: 'Google Chrome' if s == 'Chrome' else s)
        if debug:
            print(df)
        return df

    @staticmethod
    def get_orders_for_col_tree() -> dict:
        return {
            ('age', ): (0, Sort.VAL),
            # ('browser', 'age', ): (1, Sort.LBL, 0, Sort.INCREASING),  ## TODO - will need to manually check what expected results should be (groan)
            # ('browser', 'car', ): (1, Sort.LBL, 1, Sort.DECREASING),
            ('browser', 'age', ): (1, Sort.LBL, 0, Sort.VAL),
            ('browser', 'car', ): (1, Sort.LBL, 1, Sort.LBL),
        }

    @staticmethod
    def tuple2branch_of_vars_key(orig_tuple: tuple, *, debug=False) -> tuple:
        """
        e.g. ('browser', 'Firefox', 'car', 'AUDI', Metric.FREQ)
        =>
        ('browser', 'car', )

        ('age', '20-29', BLANK, BLANK, Metric.FREQ)
        =>
        ('age', )
        """
        items = []
        for idx in count(0, 2):
            try:
                item = orig_tuple[idx]
            except IndexError:
                break
            if item in Metric or item == BLANK:
                break
            items.append(item)
            if debug:
                print(f"{idx=}")
            if idx > 1_000:
                raise Exception(
                    "Seriously?! Over 1,000 items in multi-index tuple?! Something has gone badly wrong! Abort!!")
        items = tuple(items)
        if debug:
            print(f"{orig_tuple} => {items}")
        return tuple(items)

    @staticmethod
    def get_lbl2val(*, debug=False) -> dict[tuple[str, str], Any]:
        age = {1: '< 20', 2: '20-29', 3: '30-39', 4: '40-64', 5: '65+'}
        car = {
            1: 'BMW',
            2: 'PORSCHE',
            3: 'AUDI',
            4: 'MERCEDES',
            5: 'VOLKSWAGEN',
            6: 'FERRARI',
            7: 'FIAT',
            8: 'LAMBORGHINI',
            9: 'MASERATI',
            10: 'HONDA',
            11: 'TOYOTA',
            12: 'MITSUBISHI',
            13: 'NISSAN',
            14: 'MAZDA',
            15: 'SUZUKI',
            16: 'DAIHATSU',
            17: 'ISUZU',
        }
        lbl_mapping = {}
        age_lbl2val = {('age', lbl): val for val, lbl in age.items()}
        browser_lbl2val = {('browser', lbl): lbl for lbl in ['Google Chrome', 'Firefox', 'Internet Explorer', 'Opera', 'Safari', ]}
        browser_lbl2val[('browser', 'Google Chrome')] = 'Chrome'
        car_lbl2val = {('car', lbl): val for val, lbl in car.items()}
        lbl_mapping.update(age_lbl2val)
        lbl_mapping.update(browser_lbl2val)
        lbl_mapping.update(car_lbl2val)
        if debug:
            print(lbl_mapping)
        return lbl_mapping

    @staticmethod
    def get_metric2order(metric: Metric) -> int:
        return {Metric.FREQ: 1, Metric.ROW_PCT: 2, Metric.COL_PCT: 3}[metric]

    @staticmethod
    def by_freq(variable: str, lbl: str, df: pd.DataFrame, filts: tuple[tuple[str, str]] | None = None, *,
            increasing=True) -> float:
        df_filt = df.copy().loc[df[variable] == lbl]
        for filt_variable, filt_lbl in filts:
            df_filt = df_filt.loc[df_filt[filt_variable] == filt_lbl]
        freq = len(df_filt)
        if increasing:
            sort_val = freq
        else:
            try:
                sort_val = 1 / freq
            except ZeroDivisionError as e:
                sort_val = 1.1  ## so always at end after lbls with freq of at least one (given we are decreasing)
        return sort_val

    @staticmethod
    def get_tuple_for_sorting(orig_tuple: tuple, *, debug=False) -> tuple:
        """
        Use this method for they key arg for sorting
        such as sorting(unsorted_multi_index_list, key=SortUtils.get_tuple_for_sorting)

        E.g.
        ('age', '<20', '__blank__', '__blank__', 'freq')
        =>
        (0, 1, 0, 0, 1)

        ('age', '65+', '__blank__', '__blank__', 'row pct')
        =>
        (0, 5, 0, 0, 2)
        """
        max_idx = len(orig_tuple) - 1
        metric_idx = max_idx
        orders_for_col_tree = SortUtils.get_orders_for_col_tree()
        branch_of_variables_key = SortUtils.tuple2branch_of_vars_key(orig_tuple, debug=debug)
        orders_spec = orders_for_col_tree[branch_of_variables_key]  ## e.g. (1, Sort.LBL, 0, Sort.INCREASING)
        lbl2val = SortUtils.get_lbl2val(debug=debug)
        list_for_sorting = []
        variable_value_pairs = []
        if debug:
            print(f"{orig_tuple=}; {max_idx=}; {orders_spec=}")
        for idx in count():
            if idx > max_idx:
                break
            ## get order for sorting
            var_idx = (idx % 2 == 0 and idx != metric_idx)
            val_idx = (idx != var_idx and idx != metric_idx)
            if var_idx:
                variable = orig_tuple[idx]
                if variable == BLANK:
                    variable_order = 0  ## never more than one so no order
                else:
                    variable_order = orders_spec[idx]
                if debug:
                    print(f"{variable=}; {variable_order=}")
                list_for_sorting.append(variable_order)
            elif val_idx:
                variable = orig_tuple[idx - 1]
                lbl = orig_tuple[idx]
                if lbl == BLANK:
                    value_order = 0  ## never more than one so no order
                else:
                    value_order_spec = orders_spec[idx]
                    if value_order_spec == Sort.LBL:
                        value_order = lbl
                    elif value_order_spec == Sort.VAL:
                        value_order = lbl2val[(variable, lbl)]
                    elif value_order_spec in (Sort.INCREASING, Sort.DECREASING):
                        raw_df = SortUtils.get_raw_df(debug=debug)
                        increasing = (value_order_spec == Sort.INCREASING)
                        filts = tuple(variable_value_pairs)
                        value_order = SortUtils.by_freq(variable, lbl, df=raw_df, filts=filts, increasing=increasing)  ## can't use df as arg for cached function
                    else:
                        raise ValueError(f"Unexpected value order spec ({value_order_spec})")
                    variable_value_pairs.append((variable, lbl))
                list_for_sorting.append(value_order)
            elif metric_idx:
                metric = orig_tuple[idx]
                metric_order = SortUtils.get_metric2order(metric)
                list_for_sorting.append(metric_order)
            else:
                raise ValueError(f"Unexpected item index ({idx=}) when getting tuple for sorting")
        tuple_for_sorting = tuple(list_for_sorting)
        return tuple_for_sorting


def get_sorted_multi_index_list(unsorted_multi_index_list: list[tuple], *, debug=False) -> list[tuple]:
    multi_index_sort_fn = partial(SortUtils.get_tuple_for_sorting, debug=debug)
    sorted_multi_index_list = sorted(unsorted_multi_index_list, key=multi_index_sort_fn)
    if debug:
        for row in sorted_multi_index_list:
            print(row)
    return sorted_multi_index_list

if __name__ == '__main__':
    unsorted_multi_index_list_a = [
        ('browser', 'Google Chrome', 'car', 'BMW', Metric.FREQ),
        ('browser', 'Google Chrome', 'car', 'PORSCHE', Metric.FREQ),
        ('browser', 'Google Chrome', 'car', 'LAMBORGHINI', Metric.FREQ),
        ('browser', 'Google Chrome', 'car', 'AUDI', Metric.FREQ),
        ('browser', 'Firefox', 'car', 'AUDI', Metric.FREQ),
        ('age', '20-29', BLANK, BLANK, Metric.FREQ),
        ('age', '65+', BLANK, BLANK, Metric.FREQ),
        ('age', '30-39', BLANK, BLANK, Metric.FREQ),
        ('browser', 'Firefox', 'age', '< 20', Metric.FREQ),
        ('browser', 'Firefox', 'age', '20-29', Metric.FREQ),
        ('browser', 'Firefox', 'age', '30-39', Metric.FREQ),
        ('browser', 'Firefox', 'age', '40-64', Metric.FREQ),
        ('age', '< 20', BLANK, BLANK, Metric.FREQ),
        ('browser', 'Firefox', 'age', '65+', Metric.FREQ),
        ('browser', 'Google Chrome', 'age', '< 20', Metric.FREQ),
        ('browser', 'Google Chrome', 'age', '20-29', Metric.FREQ),
        ('age', '40-64', BLANK, BLANK, Metric.FREQ),
        ('browser', 'Firefox', 'car', 'PORSCHE', Metric.FREQ),
        ('browser', 'Firefox', 'car', 'LAMBORGHINI', Metric.FREQ),
        ('browser', 'Google Chrome', 'age', '30-39', Metric.FREQ),
        ('browser', 'Google Chrome', 'age', '65+', Metric.FREQ),
        ('browser', 'Firefox', 'car', 'BMW', Metric.FREQ),
        ('browser', 'Google Chrome', 'age', '40-64', Metric.FREQ),
    ]
    get_sorted_multi_index_list(unsorted_multi_index_list_a, debug=True)
