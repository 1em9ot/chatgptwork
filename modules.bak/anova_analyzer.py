import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def analyze_anova(csv_file="sample_anova.csv", output_image="anova_boxplot.png"):
    """
    CSVファイルは、少なくとも2つ以上のグループのデータを含むことが前提です。
    CSVファイルは 'group' と 'value' という列を持つ形式で、各行が各グループの観測値です。

    1元配置分散分析（ANOVA）を実施し、F統計量とp値をログに出力。
    また、各グループの箱ひげ図を作成して output_image に保存します。
    """
    try:
        data = pd.read_csv(csv_file)
        logging.info(f"CSV file '{csv_file}' read successfully.")
    except Exception as e:
        logging.error(f"Failed to read CSV file '{csv_file}': {e}")
        return

    # 必要なカラムが存在するかチェック
    if "group" not in data.columns or "value" not in data.columns:
        logging.error(f"CSV file '{csv_file}' must contain 'group' and 'value' columns.")
        return

    # グループごとに値をリスト化
    groups = data.groupby("group")["value"].apply(list)
    if len(groups) < 2:
        logging.error("ANOVA requires at least two groups.")
        return

    try:
        f_stat, p_value = stats.f_oneway(*groups)
        logging.info(f"ANOVA results: F-statistic = {f_stat:.3f}, p-value = {p_value:.3f}")
    except Exception as e:
        logging.error(f"Error performing ANOVA: {e}")
        return

    # 箱ひげ図の作成
    try:
        plt.figure(figsize=(10, 6))
        data.boxplot(column="value", by="group", grid=False)
        plt.title("ANOVA Boxplot by Group")
        plt.suptitle("")  # デフォルトタイトルを削除
        plt.xlabel("Group")
        plt.ylabel("Value")
        plt.tight_layout()
        plt.savefig(output_image)
        plt.close()
        logging.info(f"ANOVA boxplot saved as '{output_image}'")
    except Exception as e:
        logging.error(f"Error generating or saving boxplot: {e}")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("Starting ANOVA Analyzer")
    analyze_anova()
    logging.info("ANOVA analysis completed.")

if __name__ == "__main__":
    main()
