
from enum import StrEnum

BLANK = '__blank__'

class Metric(StrEnum):
    FREQ = 'Freq'
    ROW_PCT = 'Row %'
    COL_PCT = 'Col %'

PCT_METRICS = [Metric.ROW_PCT, Metric.COL_PCT]

class Sort(StrEnum):
    LBL = 'by label'
    VAL = 'by value'
    INCREASING = 'by increasing freq'
    DECREASING = 'by decreasing freq'
