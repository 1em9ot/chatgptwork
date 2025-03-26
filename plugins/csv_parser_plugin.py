import csv
import logging
from interfaces import IParser

PLUGIN_NAME = "CSVParser"

class CSVParser(IParser):
    def parse(self, file_path: str, encoding: str = 'utf-8'):
        logging.info(f"Parsing CSV file: {file_path}")
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                data = list(reader)
            logging.info(f"CSV parsing successful, {len(data)} records found")
            return data
        except Exception as e:
            logging.error(f"CSV parsing failed for {file_path}: {e}")
            raise

    def supported_extensions(self) -> list:
        return ['.csv']
