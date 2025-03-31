import os
import csv
import logging
from scipy import stats

def analyze_t_test(csv_file="sample_stat.csv"):
    """
    CSVファイルは、ヘッダーに "group1" と "group2" を持つ2群の数値データを含む形式であることを前提とします。
    各行は2群の対応する観測値となります。
    """
    group1 = []
    group2 = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "group1" in row and "group2" in row:
                    try:
                        group1.append(float(row["group1"]))
                        group2.append(float(row["group2"]))
                    except ValueError:
                        continue  # 数値に変換できない場合はスキップ
        if not group1 or not group2:
            logging.error("t検定に必要なデータが不足しています。")
            return
        # 独立サンプルのt検定を実施
        t_stat, p_val = stats.ttest_ind(group1, group2)
        logging.info(f"t検定結果: t統計量 = {t_stat:.3f}, p値 = {p_val:.3f}")
    except Exception as e:
        logging.error(f"t検定解析中にエラーが発生しました: {e}")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Statistical Test Analyzer の開始")
    analyze_t_test()
    logging.info("Statistical Test Analysis 完了")

if __name__ == "__main__":
    main()
