import json
import logging
from interfaces import IConfigManager

class ConfigManager(IConfigManager):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.config = {}

    def load_config(self, path: str) -> None:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logging.info(f"Config loaded successfully from {path}")
        except Exception as e:
            logging.error(f"Failed to load config from {path}: {e}")

    def get(self, key: str, default=None):
        value = self.config.get(key, default)
        logging.debug(f"Config get: key={key}, value={value}")
        return value
