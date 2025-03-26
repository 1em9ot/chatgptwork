from abc import ABC, abstractmethod

class IConfigManager(ABC):
    @abstractmethod
    def load_config(self, path: str) -> None:
        """指定されたパスから設定を読み込む"""
        pass

    @abstractmethod
    def get(self, key: str, default=None):
        """指定キーの設定値を返す。なければdefaultを返す"""
        pass

class ILogger(ABC):
    @abstractmethod
    def setup_logging(self, log_dir: str, log_level: str) -> None:
        """ログディレクトリとログレベルを指定してログの初期化を行う"""
        pass

    @abstractmethod
    def log(self, level: str, message: str) -> None:
        """指定されたレベルでメッセージをログ出力する"""
        pass

class IDBConnector(ABC):
    @abstractmethod
    def connect(self, db_path: str):
        """データベースへの接続を初期化する"""
        pass

    @abstractmethod
    def execute(self, query: str, params: tuple = ()):
        """クエリを実行し、結果を返す"""
        pass

    @abstractmethod
    def commit(self) -> None:
        """トランザクションをコミットする"""
        pass

    @abstractmethod
    def close(self) -> None:
        """接続を閉じる"""
        pass

class IParser(ABC):
    @abstractmethod
    def parse(self, file_path: str, encoding: str = 'utf-8'):
        """指定されたファイルをパースし、辞書のリストを返す"""
        pass

    @abstractmethod
    def supported_extensions(self) -> list:
        """このパーサーがサポートする拡張子のリストを返す"""
        pass

# interfaces.py の末尾あたりに追記

class IAnalysis(ABC):
    @abstractmethod
    def analyze(self, data: list, **kwargs) -> dict:
        """
        データを受け取り、何らかの解析結果を返す。
        dataはCSVなどから読み込んだ辞書リストを想定。
        戻り値は、解析結果を辞書形式で返す想定。
        """
        pass
