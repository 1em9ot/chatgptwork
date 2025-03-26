import json
import logging
from interfaces import IParser

PLUGIN_NAME = "JSONParser"

class JSONParser(IParser):
    def parse(self, file_path: str, encoding: str = 'utf-8'):
        logging.info(f"Parsing JSON file: {file_path}")
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            logging.info("JSON parsing successful")
            return data
        except Exception as e:
            logging.error(f"JSON parsing failed for {file_path}: {e}")
            raise

    def supported_extensions(self) -> list:
        return ['.json']
