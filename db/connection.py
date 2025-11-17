import sqlite3
from contextlib import contextmanager
from pathlib import Path

SETTING_DATABASE_NAME = "mlb.db"
SETTING_DATABASE_PATH = Path(__file__).parent / SETTING_DATABASE_NAME


class ConnectionManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    @contextmanager
    def transaction(self):
        self.connect()
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def execute(self, sql, params=()):
        self.connect()
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def query(self, sql, params=()):
        cur = self.execute(sql, params)
        return cur.fetchall()
