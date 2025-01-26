"""
TODO: use these in places where hardwired in variable labels, value labels, pandas var names etc. Also in chart demos etc

You want a label for a variable, a value, or even the Pandas variable name to use when processing a variable
inside intermediate tables, you come here.
"""
from dataclasses import dataclass
from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML(typ='safe')   # default, if not specified, is 'rt' (round-trip)

@dataclass(kw_only=True)
class VarLabels:
    name: str
    lbl: str
    comment: str | None = None
    val2lbl: dict[int | str, str]  ## OK to have missing mappings (even an empty dict is OK) - in which case the lbl will be the str representation of the value

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

def yaml2varlabels(yaml_fpath: Path, *, debug=False) -> dict[str, VarLabels]:
    raw_yaml = yaml.load(yaml_fpath)
    var_labels = {}
    for var, var_spec in raw_yaml.items():
        kwargs = {
            'name': var,
            'lbl': var_spec.get('var_lbl', var),
            'val2lbl': var_spec.get('val_lbls', {}),
        }
        if var_spec.get('var_comment'):
            kwargs['comment'] = var_spec.get('var_comment')
        var_labels_spec = VarLabels(**kwargs)
        var_labels[var] = var_labels_spec
    if debug:
        print(raw_yaml)
        for var, var_lbls in var_labels.items():
            print(f"{var}:\n  {var_lbls}")
        print()
    return var_labels

if __name__ == '__main__':
    yaml_fpath = Path(__file__).parent.parent.parent.parent / 'store' / 'var_labels.yaml'
    yaml2varlabels(yaml_fpath, debug=True)
