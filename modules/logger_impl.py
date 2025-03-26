import logging
from interfaces import ILogger

class Logger(ILogger):
    def setup_logging(self, log_dir: str, log_level: str, private: bool = True) -> None:
        try:
            # privateフラグがTrueの場合、サブフォルダを作成せず、カレントディレクトリにログファイルを作成
            if private:
                log_file = "private_app.log"
            else:
                log_file = "app.log"

            logging.basicConfig(
                level=getattr(logging, log_level.upper(), logging.INFO),
                format='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                handlers=[logging.FileHandler(log_file, encoding='utf-8'),
                          logging.StreamHandler()]
            )
            logging.info(f"Logging initialized in {log_file} at level {log_level}")
        except Exception as e:
            print(f"Logging initialization failed: {e}")

    def log(self, level: str, message: str) -> None:
        if level.lower() == 'info':
            logging.info(message)
        elif level.lower() == 'error':
            logging.error(message)
        elif level.lower() == 'warning':
            logging.warning(message)
        elif level.lower() == 'debug':
            logging.debug(message)
        else:
            logging.info(message)
