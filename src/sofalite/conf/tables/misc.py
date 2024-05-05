
from enum import StrEnum

BLANK = '__blank__'

class Measure(StrEnum):
    FREQ = 'Freq'
    ROW_PCT = 'Row %'
    COL_PCT = 'Col %'

PCT_MEASURES = [Measure.ROW_PCT, Measure.COL_PCT]
