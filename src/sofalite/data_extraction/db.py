"""
Either pass in a CSV or a cursor. If the cursor is not for SQLite, must also pass in a DBSpec.
The DbSpec enables db-specific quoting e.g. to make a frequency table of a variable containing strings
we would need to be able to quote and escape the content.

Only internal SQLite (for CSV ingestion) requires us to close off cursors and connections.
Otherwise, that is an external responsibility.
"""
from pathlib import Path
import sqlite3 as sqlite
from textwrap import dedent

from ruamel.yaml import YAML

from sofalite.conf.main import CUSTOM_DBS_FOLDER, DbeName, DbeSpec

yaml = YAML(typ='safe')  ## default, if not specified, is 'rt' (round-trip)

class ExtendedCursor:

    def __init__(self, cur):
        self.cur = cur

    def exe(self, sql):
        try:
            self.cur.execute(sql)
        except Exception as e:
            raise Exception(dedent(f"""
            Error: {e}

            Original SQL:
            {sql}
            """))

    def __getattr__(self, method_name):  ## delegate everything to real cursor
        method = getattr(self.cur, method_name)
        return method


class Sqlite:  ## TODO kill once Source takes over everywhere

    def __init__(self, database: Path):
        self.database = database

    def __enter__(self) -> tuple:
        self.con = sqlite.connect(self.database)
        self.cur = ExtendedCursor(self.con.cursor())
        return self.con, self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.con.close()


def _yaml_to_dbe_spec(*, yaml_dict: dict[str, str]) -> DbeSpec:
    y = yaml_dict
    return DbeSpec(
        if_clause=y['if_clause'],
        placeholder=y['placeholder'],
        left_obj_quote=y['left_obj_quote'],
        right_obj_quote=y['right_obj_quote'],
        gte_not_equals=y['gte_not_equals'],
        cartesian_joiner=y['cartesian_joiner'],
        sql_str_literal_quote=y['sql_str_literal_quote'],
        sql_esc_str_literal_quote=y['sql_esc_str_literal_quote'],
        summable=y['summable'],
    )

std_dbe_name2spec = {
    DbeName.SQLITE: DbeSpec(
            if_clause='CASE WHEN %s THEN %s ELSE %s END',
            placeholder='?',
            left_obj_quote='`',
            right_obj_quote='`',
            gte_not_equals='!=',
            cartesian_joiner=' JOIN ',
            sql_str_literal_quote="'",
            sql_esc_str_literal_quote="''",
            summable='',
        )
}

def _get_std_dbe_spec(dbe_name: DbeName | str) -> DbeSpec:
    return std_dbe_name2spec.get(dbe_name)

def get_db_spec(dbe_name: str, *, debug=False) -> DbeSpec:
    db_spec = _get_std_db_spec(dbe_name)
    if not db_spec:
        ## look for custom YAML file
        yaml_fpath = CUSTOM_DBS_FOLDER / f"{dbe_name}.yaml"
        try:
            yaml_dict = yaml.load(yaml_fpath)
        except FileNotFoundError as e:
            e.add_note(f"Unable to open {yaml_fpath} to extract database engine specification for '{dbe_name}'")
            raise
        except Exception as e:
            e.add_note(f"Experienced a problem extracting database engine information from '{yaml_fpath}'")
            raise
        else:
            if debug: print(yaml_dict)
            try:
                dbe_spec = _yaml_to_dbe_spec(yaml_dict=yaml_dict)
            except KeyError as e:
                e.add_note(f"Unable to create database engine spec from '{yaml_fpath}'")
                raise
    return dbe_spec
