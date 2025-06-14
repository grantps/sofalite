from dataclasses import asdict, dataclass, fields
import re

from sofalite import SQLITE_DB

def pluralise_with_s(singular, n):
    return singular if n == 1 else f'{singular}s'

def todict(dc: dataclass, *, shallow=True) -> dict:
    """
    dataclasses.asdict is recursive i.e. if you have an internal sequence of dataclasses
    then they will be transformed into dicts as well.
    todict is shallow by default in which case it only turns the top level into a dict.
    This might be useful if wanting to feed the contents of the dataclass into another dataclass
    e.g. anova_results_extended = AnovaResultsExtended(**todict(anova_results), ...)
    where the goal is to make a new dataclass that has everything in the parent class
    plus new items in the child class.
    """
    if shallow:
        dict2use = dict((field.name, getattr(dc, field.name)) for field in fields(dc))
    else:
        dict2use = asdict(dc)
    return dict2use

def close_internal_db():
    """
    For tidy programmers :-)
    """
    if SQLITE_DB.get('sqlite_default_cur'):
        SQLITE_DB.get['sqlite_default_cur'].close()
        SQLITE_DB.get['sqlite_default_con'].close()

def get_safer_name(raw_name):
    return re.sub('[^A-Za-z0-9]+', '_', raw_name)
