import os
import sys
import shutil
import json
import subprocess
import logging

# ログ設定: ファイル (main.log) とコンソールの両方にINFOレベル以上を出力
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('main.log', mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def ensure_folder_consistency():
    """modulesフォルダのバックアップ・重複整理・設定修正を実施する"""
    backup_success = True
    # 1. modules/ ディレクトリのバックアップ（modules.bak/ に保存）
    if os.path.exists("modules"):
        if os.path.exists("modules.bak"):
            try:
                shutil.rmtree("modules.bak")
                logger.info("古いバックアップ modules.bak/ を削除しました。")
            except Exception as e:
                logger.warning(f"古い modules.bak/ の削除に失敗しました: {e}")
        try:
            shutil.copytree("modules", "modules.bak")
            logger.info("modules/ を modules.bak/ にバックアップしました。")
        except Exception as e:
            logger.error(f"modules/ のバックアップに失敗しました: {e}")
            backup_success = False
    else:
        logger.info("modules/ ディレクトリが存在しません（初回実行または既に移動済み）。")

    if not backup_success:
        # バックアップが取れない場合は安全のため中断
        return False

    # 2. 重複フォルダ modules(1)/ の整理・統合
    if os.path.exists("modules(1)"):
        logger.info("重複フォルダ modules(1)/ が存在します。統合処理を実行します。")
        if not os.path.exists("modules"):
            # modules/ が無ければ modules(1)/ をリネーム
            try:
                os.rename("modules(1)", "modules")
                logger.info("modules(1)/ を modules/ にリネームしました。")
            except Exception as e:
                logger.error(f"modules(1)/ を modules/ にリネームできませんでした: {e}")
                # リネームに失敗した場合はコピーで対処
                if not os.path.exists("modules"):
                    try:
                        shutil.copytree("modules(1)", "modules")
                        logger.info("modules(1)/ を modules/ にコピーしました。")
                    except Exception as e2:
                        logger.error(f"modules(1)/ から modules/ へのコピーに失敗しました: {e2}")
        else:
            # modules/ が存在する場合、modules(1)/ 内のファイルを modules/ に統合
            for root, dirs, files in os.walk("modules(1)"):
                rel_path = os.path.relpath(root, "modules(1)")
                target_dir = "modules" if rel_path == "." else os.path.join("modules", rel_path)
                if not os.path.exists(target_dir):
                    try:
                        os.makedirs(target_dir, exist_ok=True)
                    except Exception as e:
                        logger.warning(f"ディレクトリ {target_dir} の作成に失敗しました: {e}")
                for file in files:
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(target_dir, file)
                    try:
                        if os.path.exists(dest_path):
                            os.remove(dest_path)
                            logger.info(f"既存のファイル {dest_path} を削除して上書きします。")
                        shutil.move(src_path, dest_path)
                        logger.info(f"{src_path} を {dest_path} に移動しました。")
                    except Exception as e:
                        logger.error(f"ファイル {src_path} の統合に失敗しました: {e}")
            # 統合後、modules(1)/ フォルダを削除
            try:
                shutil.rmtree("modules(1)")
                logger.info("統合完了後、modules(1)/ フォルダを削除しました。")
            except Exception as e:
                logger.error(f"modules(1)/ フォルダの削除に失敗しました: {e}")
    else:
        logger.info("重複フォルダ modules(1)/ は存在しません。")

    # 3. modules/ フォルダ内のファイルチェック（必要なファイルが無い場合はバックアップから復元）
    if os.path.exists("modules"):
        py_files = [f for f in os.listdir("modules") if f.endswith(".py")]
        if len(py_files) == 0:
            if os.path.exists("modules.bak"):
                logger.warning("modules/ フォルダ内に .py ファイルが見つかりません。バックアップから復元します。")
                try:
                    shutil.rmtree("modules")
                except Exception as e:
                    logger.error(f"空の modules/ フォルダの削除に失敗しました: {e}")
                try:
                    shutil.copytree("modules.bak", "modules")
                    logger.info("バックアップから modules/ を復元しました。")
                except Exception as e:
                    logger.error(f"バックアップから modules/ の復元に失敗しました: {e}")
            else:
                logger.error("modules/ フォルダが空で、バックアップも存在しません。")
    else:
        logger.warning("modules/ フォルダが存在しません。")

    # 4. config.json 内 gist_files のパス修正（modules(1)/ -> modules/）
    config_path = "config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"config.json の読み込みに失敗しました: {e}")
            config = None
        if config and "gist_files" in config:
            gist_files = config["gist_files"]
            updated = False
            if isinstance(gist_files, list):
                new_list = []
                for path in gist_files:
                    if isinstance(path, str):
                        new_path = path
                        # modules(1)/ を modules/ に置換
                        if "modules(1)" in new_path:
                            new_path = new_path.replace("modules(1)", "modules")
                            updated = True
                            logger.info(f"gist_files 修正: {path} -> {new_path}")
                        # .pyファイル（main.py, update_gist.py以外）は modules/ 配下に統一
                        if new_path.endswith(".py") and new_path not in ("main.py", "update_gist.py") and not new_path.startswith("modules/"):
                            new_path = os.path.join("modules", os.path.basename(new_path))
                            updated = True
                            logger.info(f"gist_files エントリを modules/ 配下に修正: {path} -> {new_path}")
                        new_list.append(new_path)
                    else:
                        new_list.append(path)
                # 重複エントリを削除
                unique_list = []
                seen = set()
                for p in new_list:
                    if p not in seen:
                        unique_list.append(p)
                        seen.add(p)
                if len(unique_list) != len(new_list):
                    updated = True
                    logger.info("gist_files 内の重複エントリを削除しました。")
                if updated:
                    config["gist_files"] = unique_list
            elif isinstance(gist_files, dict):
                # 辞書形式の場合も modules(1) を modules に置換し、必要ならパスを修正
                for key, path in list(gist_files.items()):
                    if isinstance(path, str):
                        new_path = path
                        if "modules(1)" in new_path:
                            new_path = new_path.replace("modules(1)", "modules")
                            updated = True
                            logger.info(f"gist_files 修正: {path} -> {new_path}")
                        if new_path.endswith(".py") and new_path not in ("main.py", "update_gist.py") and not new_path.startswith("modules/"):
                            new_path = os.path.join("modules", os.path.basename(new_path))
                            updated = True
                            logger.info(f"gist_files エントリを modules/ 配下に修正: {path} -> {new_path}")
                        config["gist_files"][key] = new_path
            if updated:
                try:
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    logger.info("config.json の gist_files エントリを更新しました。")
                except Exception as e:
                    logger.error(f"config.json の更新書き込みに失敗しました: {e}")
                    return False
        else:
            logger.info("config.json に gist_files エントリが見つかりません。")
    else:
        logger.info("config.json が存在しないため、gist_files の更新はスキップします。")
    return True

def move_py_files():
    """main.py・config.json・update_gist.py を除く全ての .py ファイルを modules/ に移動"""
    modules_dir = "modules"
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir, exist_ok=True)
        logger.info(f"{modules_dir}/ ディレクトリを作成しました。")
    for filename in os.listdir("."):
        if filename.endswith(".py") and filename not in ("main.py", "config.json", "update_gist.py"):
            src = filename
            dst = os.path.join(modules_dir, filename)
            try:
                if os.path.exists(dst):
                    logger.warning(f"{dst} が既に存在します。{filename} の移動をスキップします。")
                else:
                    shutil.move(src, dst)
                    logger.info(f"{filename} を {dst} に移動しました。")
            except Exception as e:
                logger.error(f"{filename} の移動中にエラーが発生しました: {e}")
                return False
    return True

def run_tests():
    """unittest を実行し、成功なら True を返す"""
    try:
        result = subprocess.run(["python", "-m", "unittest", "discover"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"ユニットテスト失敗:\n{result.stdout}\n{result.stderr}")
            return False
        logger.info("ユニットテスト成功。")
        return True
    except Exception as e:
        logger.error(f"ユニットテスト実行中に例外が発生しました: {e}")
        return False

def update_gist():
    """update_gist.py を実行して Gist を更新する"""
    try:
        result = subprocess.run(["python", "update_gist.py"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Gist 更新スクリプトでエラー発生 (戻り値 {result.returncode}):\n{result.stdout}\n{result.stderr}")
            return False
        logger.info("Gist を更新しました。")
        return True
    except Exception as e:
        logger.error(f"Gist の更新処理中に例外が発生しました: {e}")
        return False

def restore_modules_and_config():
    """modules/ および config.json をバックアップから復元"""
    if os.path.exists("modules.bak"):
        try:
            if os.path.exists("modules"):
                shutil.rmtree("modules")
            shutil.copytree("modules.bak", "modules")
            logger.info("バックアップから modules/ を復元しました。")
        except Exception as e:
            logger.error(f"modules/ の復元に失敗しました: {e}")
    else:
        logger.error("modules.bak/ が存在しないため modules/ を復元できません。")
    if os.path.exists("config.json.bak"):
        try:
            shutil.copy2("config.json.bak", "config.json")
            logger.info("バックアップから config.json を復元しました。")
        except Exception as e:
            logger.error(f"config.json の復元に失敗しました: {e}")
    else:
        if os.path.exists("config.json"):
            logger.error("config.json.bak が存在しないため config.json を復元できません。")
        else:
            logger.info("config.json が元々存在しないため、復元は不要です。")

if __name__ == "__main__":
    logger.info("===== main.py 開始 =====")
    # config.json のバックアップを作成
    if os.path.exists("config.json"):
        try:
            shutil.copy2("config.json", "config.json.bak")
            logger.info("config.json のバックアップを作成しました。")
        except Exception as e:
            logger.error(f"config.json のバックアップに失敗しました: {e}")
            logger.error("設定ファイルのバックアップに失敗したため処理を中断します。")
            logger.info("===== main.py 終了 (バックアップ失敗) =====")
            sys.exit(1)
    # フォルダ構成の整理と config.json 更新
    if not ensure_folder_consistency():
        logger.error("フォルダ構成の整合性確保中にエラーが発生しました。ロールバックを実行します。")
        restore_modules_and_config()
        logger.info("===== main.py 終了 (ロールバック実行) =====")
        sys.exit(1)
    # .pyファイルの modules/ への移動
    if not move_py_files():
        logger.error("ファイル移動中にエラーが発生しました。ロールバックを実行します。")
        restore_modules_and_config()
        logger.info("===== main.py 終了 (ロールバック実行) =====")
        sys.exit(1)
    # ユニットテストの実行
    if not run_tests():
        logger.error("ユニットテストに失敗したため、変更を元に戻します。")
        restore_modules_and_config()
        logger.info("===== main.py 終了 (ロールバック実行) =====")
        sys.exit(1)
    # テスト成功時のみ Gist を更新
    if not update_gist():
        logger.error("Gist の更新に失敗しました。変更は保持されていますが、手動での確認が必要です。")
        # Gist更新失敗時はロールバックせず、変更を保持
    logger.info("===== main.py 終了 =====")
