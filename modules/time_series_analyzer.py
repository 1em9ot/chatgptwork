import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import json

def load_config():
    """config.json から設定を読み込む。存在しなければ空の辞書を返す。"""
    config_path = os.path.join(os.getcwd(), "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        logging.info(f"Config loaded from {config_path}")
        return config
    except Exception as e:
        logging.warning(f"Could not load config file: {e}. Using default settings.")
        return {}

def analyze_time_series(csv_file="sample_timeseries.csv", output_dir="timeseries_plots"):
    """
    CSVファイルは、'date' 列（日付形式）と 'value' 列（数値）が含まれていることが前提です。
    config.json の 'ts_period' キーから季節サイクル期間を取得し、時系列データを季節性分解します。
    分解結果（トレンド、季節性、残差）のプロットを画像ファイルに保存します。
    """
    # 設定ファイルから period を取得（デフォルトは12）
    config = load_config()
    period = config.get("ts_period", 12)
    logging.info(f"Using period = {period} for time series decomposition.")

    try:
        data = pd.read_csv(csv_file, parse_dates=['date'], index_col='date')
        logging.info(f"CSV file '{csv_file}' loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load CSV file '{csv_file}': {e}")
        return

    if 'value' not in data.columns:
        logging.error(f"CSV file '{csv_file}' must contain a 'value' column.")
        return

    try:
        decomposition = seasonal_decompose(data['value'], model='additive', period=period)
        fig = decomposition.plot()
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "seasonal_decompose.png")
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()
        logging.info(f"Time series decomposition plot saved as '{output_file}'")
    except Exception as e:
        logging.error(f"Error during time series analysis: {e}")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("Starting Time Series Analyzer")
    analyze_time_series()
    logging.info("Time series analysis completed.")

if __name__ == "__main__":
    main()
