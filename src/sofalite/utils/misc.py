from dataclasses import asdict, dataclass, fields

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
