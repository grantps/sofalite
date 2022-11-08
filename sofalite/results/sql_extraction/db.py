from pathlib import Path
import sqlite3 as sqlite
from textwrap import dedent


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


class Sqlite:

    def __init__(self, database: Path):
        self.database = database

    def __enter__(self) -> tuple:
        self.con = sqlite.connect(self.database)
        self.cur = ExtendedCursor(self.con.cursor())
        return self.con, self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.con.close()
