import sqlite3
import logging
from interfaces import IDBConnector

class DBConnector(IDBConnector):
    def __init__(self):
        self.connection = None

    def connect(self, db_path: str):
        try:
            self.connection = sqlite3.connect(db_path)
            logging.info(f"Connected to DB at {db_path}")
            return self.connection
        except Exception as e:
            logging.error(f"DB connection failed for {db_path}: {e}")
            raise

    def execute(self, query: str, params: tuple = ()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            logging.debug(f"Executed query: {query} with params {params}")
            return cursor
        except Exception as e:
            logging.error(f"Query execution failed: {query}, params {params}: {e}")
            raise

    def commit(self) -> None:
        if self.connection:
            try:
                self.connection.commit()
                logging.info("DB commit successful")
            except Exception as e:
                logging.error(f"DB commit failed: {e}")
                raise

    def close(self) -> None:
        if self.connection:
            try:
                self.connection.close()
                logging.info("DB connection closed")
                self.connection = None
            except Exception as e:
                logging.error(f"Failed to close DB connection: {e}")
                raise
