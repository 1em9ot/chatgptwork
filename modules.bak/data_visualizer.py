import os
import logging
import matplotlib.pyplot as plt

def visualize_data_from_csv(csv_file="sample.csv", output_image="analysis_chart_csv.png"):
    import csv
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            ids = []
            values = []
            for row in reader:
                # 'id' と 'value' が存在することを前提
                ids.append(row.get("id"))
                values.append(float(row.get("value", 0)))
            if not ids or not values:
                logging.warning(f"No data found in {csv_file} for visualization.")
                return
        plt.figure(figsize=(10, 6))
        plt.bar(ids, values, color='skyblue')
        plt.xlabel("ID")
        plt.ylabel("Value")
        plt.title("CSV Data Visualization")
        plt.tight_layout()
        plt.savefig(output_image)
        plt.close()
        logging.info(f"CSV visualization saved as {output_image}")
    except Exception as e:
        logging.error(f"Error visualizing CSV data: {e}")

def visualize_data_from_json(json_file="sample.json", output_image="analysis_chart_json.png"):
    import json
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        items = data.get("items", [])
        if not items:
            logging.warning(f"No items found in {json_file} for visualization.")
            return
        ids = [item.get("id") for item in items]
        values = [float(item.get("value", 0)) for item in items]
        plt.figure(figsize=(10, 6))
        plt.bar(ids, values, color='lightgreen')
        plt.xlabel("ID")
        plt.ylabel("Value")
        plt.title("JSON Data Visualization")
        plt.tight_layout()
        plt.savefig(output_image)
        plt.close()
        logging.info(f"JSON visualization saved as {output_image}")
    except Exception as e:
        logging.error(f"Error visualizing JSON data: {e}")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Starting Data Visualizer")
    visualize_data_from_csv()
    visualize_data_from_json()
    logging.info("Data visualization completed.")

if __name__ == "__main__":
    main()
