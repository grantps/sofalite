from dataclasses import dataclass, field
from enum import StrEnum
from functools import cached_property
from itertools import groupby
from pathlib import Path
import platform

SOFALITE_WEB_RESOURCES_ROOT = 'http://www.sofastatistics.com/sofalite'
SOFALITE_FS_RESOURCES_ROOT = Path('/home/g/Documents/sofastats/reports/sofastats_report_extras')

class Platform(StrEnum):
    LINUX = 'linux'
    WINDOWS = 'windows'
    MAC = 'mac'

PLATFORMS = {'Linux': Platform.LINUX, 'Windows': Platform.WINDOWS, 'Darwin': Platform.MAC}
PLATFORM = PLATFORMS.get(platform.system())

@dataclass(kw_only=True)
class VarLabelSpec:
    name: str
    lbl: str | None = None
    comment: str | None = None
    val2lbl: dict[int | str, str] = field(default_factory=dict)  ## OK to have missing mappings (even an empty dict is OK) - in which case the lbl will be the str representation of the value. But no duplicates.

    def __post_init__(self):
        if self.lbl is None:
            self.lbl = self.name.title()
        val_lbls = sorted(val_lbl for val, val_lbl in self.val2lbl.items())
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

    def validate(self):
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

    def __post_init__(self):
        self.validate()

    @cached_property
    def var_and_val_lbl2val(self) -> dict[tuple[str, str], int | str]:
        """
        {(var, lbl): val, ...}
        for all variables (and their labels).
        """
        var_and_val_lbl2val = {}
        for var_label_spec in self.var_label_specs:
            for val, val_lbl in var_label_spec.val2lbl.items():
                var_and_val_lbl2val[(var_label_spec.name, val_lbl)] = val
        return var_and_val_lbl2val

    @cached_property
    def var_lbl2var(self) -> dict[str, int | str]:
        var_lbl2var = {}
        for var_label_spec in self.var_label_specs:
            var_lbl2var[var_label_spec.lbl] = var_label_spec.name
        return var_lbl2var

    @cached_property
    def var2var_label_spec(self) -> dict[str, VarLabelSpec]:
        var2var_label_spec = {}
        for var_label_spec in self.var_label_specs:
            var2var_label_spec[var_label_spec.name] = var_label_spec
        return var2var_label_spec

    @cached_property
    def var2var_lbl(self) -> dict[str, str]:
        var2var_lbl = {var: var_label_spec.lbl for var, var_label_spec in self.var2var_label_spec.items()}
        return var2var_lbl

    @cached_property
    def var2val2lbl(self) -> dict[int | str, str]:
        var2val2lbl = {var: var_label_spec.val2lbl for var, var_label_spec in self.var2var_label_spec.items()}
        return var2val2lbl

    def __str__(self) -> str:
        return '\n'.join(str(var_lbl_spec) for var_lbl_spec in self.var_label_specs)
