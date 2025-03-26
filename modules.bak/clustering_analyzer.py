import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def analyze_clustering(csv_file="sample_clustering.csv", output_image="clustering_analysis.png", n_clusters=3):
    """
    sample_clustering.csv は 'x' と 'y' の列を持つ2次元データが含まれていることを前提とします。
    KMeansクラスタリングを実施し、クラスタリング結果と中心点を画像（散布図）として出力します。
    """
    try:
        data = pd.read_csv(csv_file)
        logging.info(f"CSV file '{csv_file}' loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to read CSV file '{csv_file}': {e}")
        return

    if 'x' not in data.columns or 'y' not in data.columns:
        logging.error(f"CSV file '{csv_file}' must contain 'x' and 'y' columns.")
        return

    X = data[['x', 'y']].values

    try:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(X)
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_
        logging.info(f"KMeans clustering completed with inertia: {kmeans.inertia_:.3f}")
    except Exception as e:
        logging.error(f"Error during clustering: {e}")
        return

    try:
        plt.figure(figsize=(8, 6))
        plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', marker='o', label='Data Points')
        plt.scatter(centers[:, 0], centers[:, 1], c='red', marker='X', s=200, label='Cluster Centers')
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("KMeans Clustering Analysis")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_image)
        plt.close()
        logging.info(f"Clustering analysis plot saved as '{output_image}'")
    except Exception as e:
        logging.error(f"Error generating clustering plot: {e}")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Starting Clustering Analyzer")
    analyze_clustering()
    logging.info("Clustering analysis completed.")

if __name__ == "__main__":
    main()
