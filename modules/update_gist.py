import json
import subprocess
import logging
import sys

# ログ設定（エラーをファイルに記録）
logging.basicConfig(filename='update_gist.log', level=logging.ERROR)

try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except Exception as e:
    logging.error(f"Failed to read config.json: {e}")
    sys.exit(1)

gist_id = config.get('gist_id')
gist_files = config.get('gist_files', [])

if not gist_id or not gist_files:
    logging.error("Missing 'gist_id' or 'gist_files' in config.json.")
    sys.exit(1)

error_occurred = False
for file_name in gist_files:
    try:
        # GitHub CLI を使用して各ファイルを Gist に追加（既存なら更新）
        subprocess.run(['gh', 'gist', 'edit', gist_id, '--add', file_name], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to update Gist with file '{file_name}': {e}")
        error_occurred = True
    except Exception as e:
        logging.error(f"Unexpected error updating Gist with file '{file_name}': {e}")
        error_occurred = True

# エラーがあれば終了コード1で終了
if error_occurred:
    sys.exit(1)
