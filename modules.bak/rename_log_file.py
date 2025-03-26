import os
import logging

def rename_log_file_with_summary(log_file="private_app.log"):
    """
    指定したログファイルを読み込み、"ERROR" という文字列があれば、
    ファイル名に "ERROR" を付加し、なければ "OK" を付加してリネームする。
    既に同名のファイルが存在する場合は削除して上書きする。
    """
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if "ERROR" in content:
            summary = "ERROR"
        elif "WARNING" in content:
            summary = "WARNING"
        else:
            summary = "OK"
        new_log_file = f"private_app_{summary}.log"
        if os.path.exists(new_log_file):
            os.remove(new_log_file)
            logging.debug(f"Existing file {new_log_file} removed.")
        os.rename(log_file, new_log_file)
        logging.info(f"Log file renamed to {new_log_file} based on summary: {summary}")
    except Exception as e:
        logging.error(f"Failed to rename log file: {e}")
