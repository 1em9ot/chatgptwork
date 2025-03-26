import json

def generate_dummy_json(filename="sample.json", num_items=10):
    """
    指定された件数のダミーデータを JSON ファイルとして生成する。
    データは "items" というキーの下に、各アイテムが辞書形式で格納される。
    """
    data = {
        "items": [
            {
                "id": i,
                "name": f"Item_{i}",
                "value": i * 10
            } for i in range(1, num_items + 1)
        ]
    }
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Dummy JSON file '{filename}' generated with {num_items} items.")
    except Exception as e:
        print(f"Failed to generate dummy JSON file: {e}")

if __name__ == "__main__":
    generate_dummy_json()
