from dataclasses import dataclass
from typing import Any
from sofalite.conf.misc import StrConst

@dataclass(frozen=True)
class ValDets:
    lbl: str
    val: Any

class ValType(StrConst):
    IS_SEQ = 'is_sequence'
    IS_NULLABLE = 'is_nullable'
    DATA_ENTRY_OK = 'data_entry_ok'  ## e.g. not autonumber, timestamp etc
    IS_DEFAULT = 'is_default'
    ## test
    TEXT = 'is_text'
    TEXT_LENGTH = 'text_length'
    CHARSET = 'charset'
    ## numbers
    IS_NUMERIC = 'is_numeric'
    IS_AUTONUMBER = 'is_autonumber'
    DECIMAL_PTS = 'decimal_points'
    NUM_WIDTH = 'numeric_display_width'  ## used for column display only
    IS_NUM_SIGNED = 'is_numeric_signed'
    NUM_MIN_VAL = 'numeric_minimum_value'
    NUM_MAX_VAL = 'numeric_maximum_value'
    ## datetime
    IS_DATETIME = 'is_datetime'
