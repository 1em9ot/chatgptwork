#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import json
import subprocess
import logging

# ログ設定: ファイル (main.log) とコンソールに INFO レベル以上のログを出力
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('main.log', mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def full_cleanup():
    """
    ローカル環境を完全にクリーンアップする関数です。
    ※ tracked な変更は保持します（git reset --hard は実行しません）。
    未追跡ファイル・ディレクトリは削除します。
    """
    logging.shutdown()  # ログファイルのロック解除
    print("【全環境クリーンアップ開始】")
    
    try:
        subprocess.run(["git", "clean", "-xdf"], check=True, text=True, encoding="utf-8")
        print("未追跡ファイル・ディレクトリを削除しました。")
    except Exception as e:
        print(f"git clean に失敗しました: {e}")
    
    # バックアップフォルダとバックアップファイルの削除
    for backup_dir in ["modules.bak"]:
        if os.path.exists(backup_dir):
            try:
                shutil.rmtree(backup_dir)
                print(f"{backup_dir} を削除しました。")
            except Exception as e:
                print(f"{backup_dir} の削除に失敗しました: {e}")
    for backup_file in ["config.json.bak"]:
        if os.path.exists(backup_file):
            try:
                os.remove(backup_file)
                print(f"{backup_file} を削除しました。")
            except Exception as e:
                print(f"{backup_file} の削除に失敗しました: {e}")
    
    # __pycache__ の削除
    for root, dirs, files in os.walk(".", topdown=False):
        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                try:
                    shutil.rmtree(path)
                    print(f"{path} を削除しました。")
                except Exception as e:
                    print(f"{path} の削除に失敗しました: {e}")
    
    # desktop.ini の削除
    removed_files = []
    for root, dirs, files in os.walk(".", topdown=False):
        for f in files:
            if f.lower() == "desktop.ini":
                file_path = os.path.join(root, f)
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                    print(f"削除: {file_path}")
                except Exception as e:
                    print(f"{file_path} の削除に失敗しました: {e}")
    
    # Gitインデックスから、トラッキング中の desktop.ini を除外
    if removed_files:
        tracked_files = []
        for file in removed_files:
            result = subprocess.run(["git", "ls-files", "--error-unmatch", file],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                      text=True, encoding="utf-8")
            if result.returncode == 0:
                tracked_files.append(file)
        if tracked_files:
            try:
                subprocess.run(["git", "rm", "--cached", "-f"] + tracked_files, check=True, text=True, encoding="utf-8")
                print("Gitインデックスから desktop.ini ファイルを除外しました。")
            except Exception as e:
                print(f"Gitインデックスからの desktop.ini 除外に失敗: {e}")
    
    # .gitignore の更新（desktop.ini は既に追加済み）
    gitignore_path = ".gitignore"
    try:
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        else:
            lines = []
        if "desktop.ini" not in [line.strip() for line in lines]:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                f.write("\ndesktop.ini\n")
            print("'.gitignore' に 'desktop.ini' を追加しました。")
    except Exception as e:
        print(f".gitignore の更新に失敗しました: {e}")
    
    print("【全環境クリーンアップ終了】")

def update_gitignore_python_entries():
    """
    Pythonの一時ファイルやディレクトリを自動で .gitignore に追加する。
    例: __pycache__/, *.pyc, *.pyo
    """
    entries_to_add = ["__pycache__/", "*.pyc", "*.pyo"]
    gitignore_path = ".gitignore"
    current_lines = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            current_lines = [line.strip() for line in f.readlines()]
    else:
        current_lines = []
    new_entries = []
    for entry in entries_to_add:
        if entry not in current_lines:
            new_entries.append(entry)
    if new_entries:
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(new_entries) + "\n")
        print("'.gitignore' に Python 一時ファイルのエントリを追加しました: " + ", ".join(new_entries))
    else:
        print("'.gitignore' は既に Python 一時ファイルのエントリを含んでいます。")

def fix_test_imports():
    """
    modules/test_ast_transformer.py 内の import 文を自動修正する。
    'from ast_transformer import' を 'from modules.ast_transformer import' に変更する。
    """
    test_file = os.path.join("modules", "test_ast_transformer.py")
    if os.path.exists(test_file):
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = content.replace("from ast_transformer import", "from modules.ast_transformer import")
            if new_content != content:
                with open(test_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print("test_ast_transformer.py のインポート文を修正しました。")
        except Exception as e:
            print(f"test_ast_transformer.py の修正に失敗しました: {e}")

def move_test_files():
    """
    ファイル名に 'test' が含まれる .py ファイルは、
    直下、modules、modules.bak から問答無用で test/ フォルダへ移動する。
    """
    test_dir = "test"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print("test/ フォルダを作成しました。")
    # 直下の test ファイル
    for filename in os.listdir("."):
        if filename.endswith(".py") and "test" in filename.lower() and filename not in ("main.py", "config.json", "update_gist.py"):
            src = filename
            dst = os.path.join(test_dir, filename)
            try:
                shutil.move(src, dst)
                print(f"{filename} を {dst} に移動しました。")
            except Exception as e:
                print(f"{filename} の移動中にエラーが発生しました: {e}")
    # modules 内の test ファイル
    if os.path.exists("modules"):
        for filename in os.listdir("modules"):
            if filename.endswith(".py") and "test" in filename.lower():
                src = os.path.join("modules", filename)
                dst = os.path.join(test_dir, filename)
                try:
                    shutil.move(src, dst)
                    print(f"{filename} を {dst} に移動しました。")
                except Exception as e:
                    print(f"{filename} の移動中にエラーが発生しました: {e}")
    # modules.bak 内の test ファイル
    if os.path.exists("modules.bak"):
        for filename in os.listdir("modules.bak"):
            if filename.endswith(".py") and "test" in filename.lower():
                src = os.path.join("modules.bak", filename)
                dst = os.path.join(test_dir, filename)
                try:
                    shutil.move(src, dst)
                    print(f"{filename} を {dst} に移動しました。")
                except Exception as e:
                    print(f"{filename} の移動中にエラーが発生しました: {e}")

def ensure_init_file():
    """
    modules/ をパッケージとして扱うため、__init__.py の存在を保証する。
    """
    init_path = os.path.join("modules", "__init__.py")
    if not os.path.exists(init_path):
        try:
            with open(init_path, "w", encoding="utf-8") as f:
                f.write("# modules パッケージとして扱うための __init__.py\n")
            print("modules/__init__.py を作成しました。")
        except Exception as e:
            print(f"modules/__init__.py の作成に失敗しました: {e}")

def ensure_folder_consistency():
    """
    modules フォルダのバックアップ、重複整理、設定修正を実施する。
    """
    backup_success = True
    if os.path.exists("modules"):
        if os.path.exists("modules.bak"):
            try:
                shutil.rmtree("modules.bak")
                print("古いバックアップ modules.bak/ を削除しました。")
            except Exception as e:
                print(f"古い modules.bak/ の削除に失敗しました: {e}")
        try:
            shutil.copytree("modules", "modules.bak")
            print("modules/ を modules.bak/ にバックアップしました。")
        except Exception as e:
            print(f"modules/ のバックアップに失敗しました: {e}")
            backup_success = False
    else:
        print("modules/ ディレクトリが存在しません。")
    if not backup_success:
        return False

    if os.path.exists("modules"):
        py_files = [f for f in os.listdir("modules") if f.endswith(".py")]
        if len(py_files) == 0:
            if os.path.exists("modules.bak"):
                print("modules/ に .py ファイルが見つかりません。バックアップから復元します。")
                try:
                    shutil.rmtree("modules")
                except Exception as e:
                    print(f"modules/ の削除に失敗しました: {e}")
                try:
                    shutil.copytree("modules.bak", "modules")
                    print("バックアップから modules/ を復元しました。")
                except Exception as e:
                    print(f"modules/ の復元に失敗しました: {e}")
            else:
                print("modules/ が空で、バックアップも存在しません。")
    else:
        print("modules/ ディレクトリが存在しません。")
    if os.path.exists("modules"):
        ensure_init_file()
    return True

def move_py_files():
    """
    main.py、config.json、update_gist.py 以外の .py ファイル（"test" を含まないもの）を modules/ に移動する。
    """
    modules_dir = "modules"
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir, exist_ok=True)
        print(f"{modules_dir}/ を作成しました。")
    ensure_init_file()
    for filename in os.listdir("."):
        if (filename.endswith(".py") and filename not in ("main.py", "config.json", "update_gist.py")
            and "test" not in filename.lower()):
            src = filename
            dst = os.path.join(modules_dir, filename)
            try:
                if os.path.exists(dst):
                    print(f"{dst} が既に存在します。{filename} の移動をスキップします。")
                else:
                    shutil.move(src, dst)
                    print(f"{filename} を {dst} に移動しました。")
            except Exception as e:
                print(f"{filename} の移動中にエラーが発生しました: {e}")
                return False
    return True

def update_config():
    """
    config.json 内の gist_files エントリのパスを更新する。
    ファイル名に 'test' が含まれる場合はパスを test/ に変更する。
    """
    config_path = "config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"config.json の読み込みに失敗しました: {e}")
            return False
        if "gist_files" in config:
            updated = False
            if isinstance(config["gist_files"], list):
                new_list = []
                for path in config["gist_files"]:
                    if isinstance(path, str):
                        basename = os.path.basename(path)
                        if "test" in basename.lower():
                            new_path = os.path.join("test", basename)
                            updated = True
                        else:
                            new_path = path
                        new_list.append(new_path)
                    else:
                        new_list.append(path)
                config["gist_files"] = new_list
            elif isinstance(config["gist_files"], dict):
                for key, path in config["gist_files"].items():
                    if isinstance(path, str):
                        basename = os.path.basename(path)
                        if "test" in basename.lower():
                            config["gist_files"][key] = os.path.join("test", basename)
                            updated = True
            if updated:
                try:
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    print("config.json の更新に成功しました。")
                except Exception as e:
                    print(f"config.json の更新書き込みに失敗しました: {e}")
                    return False
        return True
    else:
        print("config.json が存在しません。")
        return False

def run_tests():
    """
    test/ フォルダ内から unittest を探索して実行する。
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "test", "-p", "*.py"],
            capture_output=True, text=True, encoding="utf-8"
        )
        if result.returncode != 0:
            print(f"ユニットテスト失敗:\n{result.stdout}\n{result.stderr}")
            return False
        print("ユニットテスト成功。")
        return True
    except Exception as e:
        print(f"ユニットテスト実行中に例外が発生しました: {e}")
        return False

def resolve_merge_conflicts():
    """
    Git merge コンフリクトが発生している場合、ユーザーに確認して old ブランチ側（ours）の内容を採用する。
    """
    try:
        result = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                                capture_output=True, text=True, encoding="utf-8", check=True)
        conflicted_files = result.stdout.splitlines()
    except Exception as e:
        print(f"merge コンフリクトの確認に失敗しました: {e}")
        return

    if conflicted_files:
        print("以下のファイルでマージコンフリクトが発生しています:")
        for f in conflicted_files:
            print(f"  {f}")
        answer = input("oldブランチのこみっとOKです。テストも成功しました。対象ブランチの内容でマージしますか? (y/n): ")
        if answer.lower() == 'y':
            for f in conflicted_files:
                try:
                    subprocess.run(["git", "checkout", "--ours", f], check=True, text=True, encoding="utf-8")
                    print(f"{f} のコンフリクトを 'ours' で解決しました。")
                except Exception as e:
                    print(f"{f} のコンフリクト解決に失敗しました: {e}")
            try:
                subprocess.run(["git", "add"] + conflicted_files, check=True, text=True, encoding="utf-8")
                subprocess.run(["git", "commit", "-m", "自動マージ解決: oldブランチの内容を採用"], check=True, text=True, encoding="utf-8")
                print("マージコンフリクトを解決し、コミットしました。")
            except Exception as e:
                print(f"マージコンフリクトのコミットに失敗しました: {e}")
        else:
            print("マージ解決がキャンセルされました。手動で解決してください。")
            return
    else:
        print("マージコンフリクトはありません。")

def auto_commit_and_push():
    """
    変更を自動でコミットし、リモートにプッシュする処理です。
    もしコミット対象がなければそのまま成功とみなします（エラー出力はしません）。
    強制プッシュは試みません。
    """
    index_lock = os.path.join(".git", "index.lock")
    if os.path.exists(index_lock):
        try:
            os.remove(index_lock)
            print("index.lock を自動で削除しました。")
        except Exception as e:
            print(f"index.lock の削除に失敗しました: {e}")
            return False
    try:
        subprocess.run(["git", "add", "-A"], check=True, text=True, encoding="utf-8")
        result_commit = subprocess.run(
            ["git", "commit", "-m", "自動コミット by main.py"],
            check=False, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        stdout_lower = (result_commit.stdout or "").lower()
        stderr_lower = (result_commit.stderr or "").lower()
        if "nothing to commit" in stdout_lower or "nothing to commit" in stderr_lower:
            print("変更はありません。自動コミットはスキップします。")
        else:
            print("自動コミット完了。")
        subprocess.run(["git", "push"], check=True, text=True, encoding="utf-8")
        print("自動コミットとプッシュが完了しました。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"通常の自動コミットまたはプッシュに失敗しました: returncode={e.returncode}\ncmd={e.cmd}\nstdout={e.output}")
        return False

def choose_merge_option(current_branch, target_branch):
    """
    マージ時のオプションをユーザーに選択させるUIを表示します。
    オプション:
      1: ローカルの一時ブランチに移行する
      2: ローカルの main ブランチにマージする
      3: リモートの同名ブランチを更新する
      4: リモートの main ブランチにマージする
    キャンセル（空入力）の場合は None を返します。
    """
    print("マージオプションを選択してください:")
    print("1: ローカルの一時ブランチに移行する")
    print("2: ローカルの main ブランチにマージする")
    print("3: リモートの同名ブランチを更新する")
    print("4: リモートの main ブランチにマージする")
    option = input("番号を入力してください (1-4、またはキャンセルなら Enter): ").strip()
    if option == "":
        print("マージがキャンセルされました。")
        return None
    try:
        option = int(option)
    except ValueError:
        print("無効な入力です。")
        return None
    if option not in [1, 2, 3, 4]:
        print("無効な選択です。")
        return None
    return option

def merge_into_target():
    """
    現在のブランチ（old側）の内容を、選択されたオプションに応じて
    マージまたは移行します。現在のブランチがターゲットブランチの場合は何もしません。
    ターゲットブランチは環境変数 TARGET_BRANCH から取得し、なければ "main" を使用します。
    ユーザーがキャンセルした場合はエラー終了せずにスキップします。
    """
    target_branch = os.environ.get("TARGET_BRANCH", "main")
    try:
        current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                                   text=True, encoding="utf-8").strip()
    except Exception as e:
        print("現在のブランチ名の取得に失敗しました:", e)
        return False
    if current_branch == target_branch:
        print(f"現在のブランチは {target_branch} です。マージは不要です。")
        return True

    option = choose_merge_option(current_branch, target_branch)
    if option is None:
        print("マージ処理をスキップします。")
        return True

    if option == 1:
        # ローカルの一時ブランチに移行する（ブランチ名を temp_ 現在のブランチ に変更）
        try:
            new_branch = "temp_" + current_branch
            subprocess.run(["git", "branch", "-m", new_branch], check=True, text=True, encoding="utf-8")
            print(f"ブランチ名を {new_branch} に変更しました。")
            subprocess.run(["git", "push", "origin", new_branch], check=True, text=True, encoding="utf-8")
            print(f"リモートに {new_branch} をプッシュしました。")
        except Exception as e:
            print("一時ブランチへの移行に失敗しました:", e)
            return False

    elif option == 2:
        # ローカルの main ブランチにマージする
        try:
            subprocess.run(["git", "checkout", target_branch], check=True, text=True, encoding="utf-8")
            subprocess.run(["git", "merge", current_branch], check=True, text=True, encoding="utf-8")
            subprocess.run(["git", "push"], check=True, text=True, encoding="utf-8")
            print(f"{target_branch} にマージし、プッシュしました。")
        except Exception as e:
            print(f"{target_branch} へのローカルマージに失敗しました:", e)
            return False
        try:
            subprocess.run(["git", "branch", "-d", current_branch], check=True, text=True, encoding="utf-8")
            subprocess.run(["git", "push", "origin", "--delete", current_branch], check=True, text=True, encoding="utf-8")
            print(f"ブランチ {current_branch} を削除しました。")
        except Exception as e:
            print(f"ブランチ {current_branch} の削除に失敗しました: {e}")

    elif option == 3:
        # リモートの同名ブランチを更新する（現在のブランチをそのままリモートにプッシュ）
        try:
            subprocess.run(["git", "push", "origin", current_branch], check=True, text=True, encoding="utf-8")
            print(f"リモートの {current_branch} ブランチを更新しました。")
        except Exception as e:
            print("リモートブランチの更新に失敗しました:", e)
            return False

    elif option == 4:
        # リモートの main ブランチにマージする
        try:
            subprocess.run(["git", "checkout", target_branch], check=True, text=True, encoding="utf-8")
            subprocess.run(["git", "merge", current_branch], check=True, text=True, encoding="utf-8")
            subprocess.run(["git", "push"], check=True, text=True, encoding="utf-8")
            print(f"リモートの {target_branch} にマージし、プッシュしました。")
        except Exception as e:
            print(f"{target_branch} へのリモートマージに失敗しました:", e)
            return False
        try:
            subprocess.run(["git", "branch", "-d", current_branch], check=True, text=True, encoding="utf-8")
            subprocess.run(["git", "push", "origin", "--delete", current_branch], check=True, text=True, encoding="utf-8")
            print(f"ブランチ {current_branch} を削除しました。")
        except Exception as e:
            print(f"ブランチ {current_branch} の削除に失敗しました: {e}")

    return True

def restore_modules_and_config():
    """
    modules/ および config.json をバックアップから復元する。
    """
    if os.path.exists("modules.bak"):
        try:
            if os.path.exists("modules"):
                shutil.rmtree("modules")
            shutil.copytree("modules.bak", "modules")
            print("バックアップから modules/ を復元しました。")
        except Exception as e:
            print(f"modules/ の復元に失敗しました: {e}")
    else:
        print("modules.bak/ が存在しないため modules/ を復元できません。")
    if os.path.exists("config.json.bak"):
        try:
            shutil.copy2("config.json.bak", "config.json")
            print("バックアップから config.json を復元しました。")
        except Exception as e:
            print(f"config.json の復元に失敗しました: {e}")
    else:
        if os.path.exists("config.json"):
            print("config.json.bak が存在しないため config.json を復元できません。")
        else:
            print("config.json が元々存在しないため、復元は不要です。")

def show_git_status():
    """現在の Git の状態を表示する"""
    try:
        result = subprocess.run(["git", "status"], capture_output=True, text=True, encoding="utf-8", check=True)
        print("=== git status ===")
        print(result.stdout)
    except Exception as e:
        print(f"git status の表示に失敗しました: {e}")

def get_current_branch():
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "--short", "HEAD"],
            capture_output=True, text=True, encoding="utf-8", check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"現在のブランチの取得に失敗しました: {e}")
        return None

if __name__ == "__main__":
    print("===== main.py 開始 =====")
    
    # 1. 全環境クリーンアップ（作業ディレクトリの変更はそのまま）
    full_cleanup()
    
    # 2. Python 一時ファイルのエントリを .gitignore に追加
    update_gitignore_python_entries()
    
    # 3. テストファイルの import 文自動修正
    fix_test_imports()
    
    # 4. 'test' が名前に含まれる .py ファイルを test/ フォルダへ移動
    move_test_files()
    
    # 5. main.py、config.json、update_gist.py 以外の .py ファイルを modules/ に移動
    if not move_py_files():
        print("ファイル移動中にエラーが発生しました。ロールバックを実行します。")
        restore_modules_and_config()
        print("===== main.py 終了 (ロールバック実行) =====")
        sys.exit(1)
    
    # 6. config.json のバックアップ作成
    if os.path.exists("config.json"):
        try:
            shutil.copy2("config.json", "config.json.bak")
            print("config.json のバックアップを作成しました。")
        except Exception as e:
            print(f"config.json のバックアップに失敗しました: {e}")
            print("設定ファイルのバックアップに失敗したため処理を中断します。")
            print("===== main.py 終了 (バックアップ失敗) =====")
            sys.exit(1)
    else:
        print("config.json が存在しないため、バックアップは不要です。")
    
    # 7. config.json の自動更新（テスト実行前の最後のステップ）
    if not update_config():
        print("config.json の更新に失敗しました。")
        sys.exit(1)
    
    # 8. test/ フォルダ内からユニットテストを実行
    if not run_tests():
        print("ユニットテストに失敗したため、変更を元に戻します。")
        restore_modules_and_config()
        print("===== main.py 終了 (ロールバック実行) =====")
        sys.exit(1)
    
    # 9. 自動コミット＆プッシュ（まずローカルの変更を確定）
    if not auto_commit_and_push():
        print("自動コミット/プッシュに失敗しました。")
        sys.exit(1)
    
    # 10. 現在のブランチがターゲットブランチ（TARGET_BRANCH, デフォルトは "main"）でない場合、リモートのターゲットブランチとマージを試みる
    current_branch = get_current_branch()
    target_branch = os.environ.get("TARGET_BRANCH", "main")
    if current_branch != target_branch:
        try:
            subprocess.run(["git", "pull", "origin", target_branch], check=True, text=True, encoding="utf-8")
            print(f"リモートの {target_branch} ブランチをマージしました。")
        except subprocess.CalledProcessError as e:
            print(f"git pull でマージコンフリクトが発生しました: {e}")
            resolve_merge_conflicts()
            if not auto_commit_and_push():
                print("自動コミット/プッシュに失敗しました。")
                sys.exit(1)
    else:
        print(f"現在のブランチは {target_branch} です。マージ操作は不要です。")
    
    # 11. merge_into_target() を実行（現在のブランチがターゲットブランチでない場合のみ）
    if current_branch != target_branch:
        if not merge_into_target():
            print("ブランチのマージ/移行処理がキャンセルまたは失敗しました。")
            # エラー終了せずにスキップします。
    # 12. git status の結果を表示
    show_git_status()
    
    print("===== main.py 終了 =====")
