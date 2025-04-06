from collections.abc import Collection
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from ruamel.yaml import YAML

from sofalite.conf.misc import VarLabelSpec, VarLabels

yaml = YAML(typ='safe')   # default, if not specified, is 'rt' (round-trip)

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

def yaml2varlabels(yaml_fpath: Path, vars2include: Collection[str], *, debug=False) -> VarLabels:
    raw_yaml = yaml.load(yaml_fpath)
    var_label_specs = []
    for var, var_spec in raw_yaml.items():
        if var not in vars2include:
            continue
        else:
            kwargs = {
                'name': var,
                'lbl': var_spec.get('var_lbl', var.title()),
                'val2lbl': var_spec.get('val_lbls', {}),
            }
            if var_spec.get('var_comment'):
                kwargs['comment'] = var_spec.get('var_comment')
            var_labels_spec = VarLabelSpec(**kwargs)
        var_label_specs.append(var_labels_spec)
    missing_vars = set(vars2include) - set(raw_yaml.keys())
    for missing_var in missing_vars:
        print(type(VarLabelSpec))
        var_labels_spec = VarLabelSpec(name=missing_var)
        var_label_specs.append(var_labels_spec)
    var_labels = VarLabels(var_label_specs)
    if debug:
        print(raw_yaml)
        print(var_labels)
    return var_labels

if __name__ == '__main__':
    my_yaml_fpath = Path(__file__).parent.parent.parent.parent / 'store' / 'var_labels.yaml'
    yaml2varlabels(my_yaml_fpath, debug=True)
