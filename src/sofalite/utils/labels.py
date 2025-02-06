"""
TODO: use these in places where hardwired in variable labels, value labels, pandas var names etc. Also in chart demos etc

You want a label for a variable, a value, or even the Pandas variable name to use when processing a variable
inside intermediate tables, you come here.
"""
from collections.abc import Collection
from dataclasses import dataclass
from functools import cached_property
from itertools import groupby
from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML(typ='safe')   # default, if not specified, is 'rt' (round-trip)

@dataclass(kw_only=True)
class VarLabelSpec:
    name: str
    lbl: str
    comment: str | None = None
    val2lbl: dict[int | str, str]  ## OK to have missing mappings (even an empty dict is OK) - in which case the lbl will be the str representation of the value. But no duplicates.

    def __post_init__(self):
        val_lbls = sorted(val_lbl for val, val_lbl in self.val2lbl)
        duplicate_lbls = [k for k, g in groupby(val_lbls) if len(list(g)) > 1]
        if duplicate_lbls:
            raise ValueError("Different values cannot share the same label. "
                f"The following labels are used more than once: {duplicate_lbls}")

    @property
    def pandas_var(self) -> str:
        """
        E.g. agegroup => agegroup_var
        """
        return f"{self.name}_var"

    @property
    def pandas_val(self) -> str:
        """
        E.g. agegroup => agegroup_val
        """
        return f"{self.name}_val"

    def __str__(self):
        comment_if_any = f"\n  comment: {self.comment}" if self.comment else ''
        val2lbls_if_any = f"\n  value to labels: {self.val2lbl}" if self.val2lbl else ''
        return f"name: {self.name}\n  label: {self.lbl}{val2lbls_if_any}{comment_if_any}"

@dataclass(frozen=True)
class VarLabels:
    var_label_specs: list[VarLabelSpec]

    def __post_init__(self):
        """
        Prevent duplicate labels for variables e.g. you can't have age => Age and agegroup => Age
        If your YAML has duplicates like this, you'll need to specify vars2include
        so you can avoid including conflicting variables in the same use case e.g. in the same Pie Chart or Table.
        """
        var_lbls = sorted(var_label_spec.lbl for var_label_spec in self.var_label_specs)
        duplicate_lbls = [k for k, g in groupby(var_lbls) if len(list(g)) > 1]
        if duplicate_lbls:
            raise ValueError("Variables cannot coexist in the Variable Label Details if they share the same label. "
                f"The following labels are used more than once: {duplicate_lbls}")

    def get_var_and_val_lbl2val(self) -> dict[tuple[str, str], int | str]:
        """
        {(var, lbl): val, ...}
        for all variables (and their labels).
        """
        lbl2val = {}
        for var_label_spec in self.var_label_specs:
            for val, val_lbl in var_label_spec.val2lbl.items():
                lbl2val[(var_label_spec.name, val_lbl)] = val
        return lbl2val

    @cached_property
    def var2var_label_spec(self) -> dict[str, VarLabelSpec]:
        var2var_label_spec = {}
        for var_label_spec in self.var_label_specs:
            var2var_label_spec[var_label_spec.name] = var_label_spec
        return var2var_label_spec

    def __str__(self) -> str:
        return '\n'.join(str(var_lbl_spec) for var_lbl_spec in self.var_label_specs)

def yaml2varlabels(yaml_fpath: Path, vars2include: Collection[str] | None = None, *, debug=False) -> VarLabels:
    raw_yaml = yaml.load(yaml_fpath)
    var_label_specs = []
    for var, var_spec in raw_yaml.items():
        if var not in vars2include:
            continue
        kwargs = {
            'name': var,
            'lbl': var_spec.get('var_lbl', var.title()),
            'val2lbl': var_spec.get('val_lbls', {}),
        }
        if var_spec.get('var_comment'):
            kwargs['comment'] = var_spec.get('var_comment')
        var_labels_spec = VarLabelSpec(**kwargs)
        var_label_specs.append(var_labels_spec)
    var_labels = VarLabels(var_label_specs)
    if debug:
        print(raw_yaml)
        print(var_labels)
    return var_labels

if __name__ == '__main__':
    my_yaml_fpath = Path(__file__).parent.parent.parent.parent / 'store' / 'var_labels.yaml'
    yaml2varlabels(my_yaml_fpath, debug=True)
