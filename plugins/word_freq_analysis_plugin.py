# plugins/word_freq_analysis_plugin.py

import logging
from interfaces import IAnalysis

PLUGIN_NAME = "WordFreqAnalysis"

class WordFreqAnalysis(IAnalysis):
    def analyze(self, data: list, **kwargs) -> dict:
        """
        data: [{'id': '1', 'name': 'Item_1', 'value': '10'}, ...] のような辞書リスト
        kwargs: その他のパラメータ（解析対象カラム名など）
        戻り値: {'top_words': [...], 'counts': {...}} のような解析結果を想定
        """
        logging.info("WordFreqAnalysis: analyze called")

        # 解析対象カラム名を指定。デフォルトは 'name'
        target_col = kwargs.get("target_col", "name")

        # 単語頻度カウンタ
        freq_map = {}

        for row in data:
            # 行に対象カラムがなければスキップ
            if target_col not in row:
                continue
            text = str(row[target_col])
            # 簡易的に空白区切りで分割
            words = text.split()
            for w in words:
                freq_map[w] = freq_map.get(w, 0) + 1

        # 出現頻度でソートした上位N件（例:10件）を取得
        sorted_items = sorted(freq_map.items(), key=lambda x: x[1], reverse=True)
        top_n = kwargs.get("top_n", 10)
        top_words = sorted_items[:top_n]

        result = {
            "top_words": top_words,  # [('Item_1', 5), ('Item_2', 3), ...] など
            "counts": freq_map       # 全単語のカウント辞書
        }
        logging.info(f"WordFreqAnalysis: result={result}")
        return result
