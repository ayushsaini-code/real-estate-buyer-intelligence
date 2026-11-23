"""Create evaluation and cluster-distribution charts from generated reports."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

evaluation = pd.read_csv(REPORTS_DIR / "cluster_evaluation.csv")
summary = pd.read_csv(REPORTS_DIR / "buyer_cluster_summary.csv")

# Silhouette comparison (supports both old and current evaluation schemas).
plt.figure(figsize=(9, 5))
if "model" in evaluation.columns:
    for model_name, group in evaluation.groupby("model"):
        plt.plot(group["n_clusters"], group["silhouette_score"], marker="o", label=model_name)
    plt.legend()
else:
    plt.plot(evaluation["n_clusters"], evaluation["silhouette_score"], marker="o")
plt.title("Silhouette Score by Clustering Model and Cluster Count")
plt.xlabel("Number of clusters")
plt.ylabel("Silhouette score")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(REPORTS_DIR / "silhouette_score.png", dpi=160)
plt.close()

# Elbow plot for K-Means.
kmeans = evaluation[evaluation["model"].eq("KMeans")] if "model" in evaluation.columns else evaluation
if "inertia" in kmeans.columns and kmeans["inertia"].notna().any():
    plt.figure(figsize=(9, 5))
    plt.plot(kmeans["n_clusters"], kmeans["inertia"], marker="o")
    plt.title("Elbow Method — K-Means")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Inertia")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "elbow_method.png", dpi=160)
    plt.close()

plt.figure(figsize=(8, 5))
plt.bar(summary["cluster"].astype(str), summary["buyer_count"])
plt.title("Buyer Distribution Across K-Means Clusters")
plt.xlabel("Cluster")
plt.ylabel("Number of buyers")
plt.tight_layout()
plt.savefig(REPORTS_DIR / "buyer_cluster_distribution.png", dpi=160)
plt.close()

print("Cluster visualizations created successfully.")
