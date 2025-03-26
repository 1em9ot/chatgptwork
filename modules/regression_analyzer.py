import os
import csv
import logging
import numpy as np
import matplotlib.pyplot as plt

def analyze_regression(csv_file="sample_regression.csv", output_image="regression_analysis.png"):
    """
    CSVファイル内の "x" と "y" の2変量データに対して線形回帰分析を実施します。
    - CSVファイルはヘッダーに "x", "y" を持つ形式で、各行がデータ点となります。
    - 線形回帰を行い、回帰直線の傾き、切片、決定係数 (R²) を計算します。
    - データ点と回帰直線をプロットし、結果を画像ファイルに保存します。
    """
    x_values = []
    y_values = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    x_values.append(float(row["x"]))
                    y_values.append(float(row["y"]))
                except ValueError:
                    continue  # 数値変換できなければスキップ
        if not x_values or not y_values:
            logging.error("No data found in CSV for regression analysis.")
            return
    except Exception as e:
        logging.error(f"Error reading CSV file {csv_file}: {e}")
        return

    # numpy 配列に変換
    x = np.array(x_values)
    y = np.array(y_values)

    # 線形回帰: np.polyfit で1次関数のフィッティング
    slope, intercept = np.polyfit(x, y, 1)
    # 回帰直線の予測値を計算
    y_pred = slope * x + intercept
    # 決定係数 R^2 を計算
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    logging.info(f"Linear Regression Results: slope = {slope:.3f}, intercept = {intercept:.3f}, R² = {r2:.3f}")

    # プロット作成
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, label="Data Points", color="blue")
    plt.plot(x, y_pred, label="Regression Line", color="red")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Linear Regression Analysis")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_image)
    plt.close()
    logging.info(f"Regression analysis plot saved as {output_image}")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("Starting Regression Analyzer")
    analyze_regression()
    logging.info("Regression analysis completed.")

if __name__ == "__main__":
    main()
