"""
TODO: do I only use my SQLite db and extended cursor or do I allow any cursor to be passed in?
  You allow non_SQLite and any variable names and value filtering you like
  and now you have to handle quoting in a per-db engine level!
  probably allow any cursor but use SQLite and its extended cursor as default if nothing supplied
  Maybe decorate all cursors? So whether we create a standard SQLite cursor or receive any dbapi cursor
  we pass it through a function and effectively decorate it.
"""

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
