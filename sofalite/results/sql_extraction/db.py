import sqlite3 as sqlite

class Sqlite:

    def __enter__(self, database) -> tuple:
        self.con = sqlite.connect(database)
        self.cur = self.con.cursor()
        return self.con, self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.con.close()

