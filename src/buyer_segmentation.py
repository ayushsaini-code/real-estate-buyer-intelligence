"""Buyer segmentation: K-Means and Hierarchical clustering.

Run from the project root:
    python src/buyer_segmentation.py

Notes:
- Age is derived from date_of_birth using the current date at run time.
- No income or net-worth field exists in the source data; wealth labels are not inferred.
- OneHotEncoder is used for the mixed-feature clustering matrix. LabelEncoder outputs
  are also saved as a reference artifact to document the requested encoding method;
  they are not used for nominal features in the clustering distance calculation.
"""
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLIENTS_FILE = PROJECT_ROOT / "data" / "processed" / "clients_cleaned.csv"
PROPERTIES_FILE = PROJECT_ROOT / "data" / "processed" / "properties_cleaned.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    clients = pd.read_csv(CLIENTS_FILE)
    properties = pd.read_csv(PROPERTIES_FILE)

    clients["date_of_birth"] = pd.to_datetime(
        clients["date_of_birth"], errors="coerce", format="mixed"
    )
    today = pd.Timestamp.today().normalize()
    clients["age"] = ((today - clients["date_of_birth"]).dt.days / 365.2425).round(1)

    sold = properties[
        properties["listing_status"].astype(str).str.strip().str.lower().eq("sold")
    ].copy()
    sold["sale_price"] = pd.to_numeric(sold["sale_price"], errors="coerce")
    sold = sold.dropna(subset=["client_ref", "sale_price"])
    sold = sold[sold["sale_price"] > 0]

    transactions = sold.groupby("client_ref").agg(
        properties_purchased=("listing_id", "nunique"),
        total_purchase_value=("sale_price", "sum"),
        average_property_price=("sale_price", "mean"),
    ).reset_index().rename(columns={"client_ref": "client_id"})

    buyers = clients.merge(transactions, on="client_id", how="inner", validate="one_to_one")
    if buyers.empty:
        raise ValueError("No buyers with completed sales matched clients.")

    categorical = [
        c for c in ["client_type", "gender", "country", "region",
                    "acquisition_purpose", "loan_applied", "referral_channel"]
        if c in buyers.columns
    ]
    numeric = [
        c for c in ["age", "satisfaction_score", "properties_purchased",
                    "total_purchase_value", "average_property_price"]
        if c in buyers.columns
    ]

    features = buyers[categorical + numeric].copy()
    for col in categorical:
        features[col] = features[col].fillna("Unknown").astype(str).str.strip()
    for col in numeric:
        features[col] = pd.to_numeric(features[col], errors="coerce")

    # Keep numeric missing values through median imputation; categorical missing -> Unknown.
    for col in numeric:
        features[col] = features[col].fillna(features[col].median())

    if len(features) < 4:
        raise ValueError("At least four matched buyers are needed for cluster comparison.")

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("numeric", StandardScaler(), numeric),
        ],
        remainder="drop",
    )
    X = preprocessor.fit_transform(features)
    if hasattr(X, "toarray"):
        X = X.toarray()

    # Save LabelEncoder reference mappings as requested in the PRD. These encodings
    # are for traceability only; OneHotEncoder is used in the distance-based model.
    label_encoded = pd.DataFrame(index=buyers.index)
    mapping_rows = []
    for col in categorical:
        le = LabelEncoder()
        label_encoded[f"{col}_label_encoded"] = le.fit_transform(features[col].astype(str))
        mapping_rows.extend(
            {"feature": col, "category": category, "label": int(code)}
            for code, category in enumerate(le.classes_)
        )
    label_encoded.insert(0, "client_id", buyers["client_id"].values)
    label_encoded.to_csv(REPORTS_DIR / "buyer_label_encoded_reference.csv", index=False)
    pd.DataFrame(mapping_rows).to_csv(REPORTS_DIR / "label_encoding_mappings.csv", index=False)

    # Evaluate K-Means with both inertia (Elbow Method) and silhouette score.
    max_k = min(8, len(features) - 1)
    rows = []
    for k in range(2, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X)
        score = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else np.nan
        rows.append({"model": "KMeans", "n_clusters": k,
                     "inertia": model.inertia_, "silhouette_score": score})
    kmeans_eval = pd.DataFrame(rows)
    if kmeans_eval.empty:
        raise ValueError("Could not evaluate K-Means cluster counts.")
    best_k = int(kmeans_eval.loc[kmeans_eval["silhouette_score"].idxmax(), "n_clusters"])
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    buyers["kmeans_cluster"] = kmeans.fit_predict(X)

    # Hierarchical clustering uses the same encoded/scaled feature matrix.
    # Ward linkage is suitable for Euclidean-distance numeric representations.
    h_rows = []
    h_best_k = best_k
    for k in range(2, max_k + 1):
        hmodel = AgglomerativeClustering(n_clusters=k, linkage="ward")
        labels = hmodel.fit_predict(X)
        score = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else np.nan
        h_rows.append({"model": "Hierarchical", "n_clusters": k,
                       "inertia": np.nan, "silhouette_score": score})
    hierarchical_eval = pd.DataFrame(h_rows)
    if hierarchical_eval["silhouette_score"].notna().any():
        h_best_k = int(hierarchical_eval.loc[
            hierarchical_eval["silhouette_score"].idxmax(), "n_clusters"
        ])
    hierarchical = AgglomerativeClustering(n_clusters=h_best_k, linkage="ward")
    buyers["hierarchical_cluster"] = hierarchical.fit_predict(X)

    evaluation = pd.concat([kmeans_eval, hierarchical_eval], ignore_index=True)
    evaluation.to_csv(REPORTS_DIR / "cluster_evaluation.csv", index=False)

    # Produce Elbow and silhouette evaluation plots for K-Means.
    plt.figure(figsize=(8, 5))
    plt.plot(kmeans_eval["n_clusters"], kmeans_eval["inertia"], marker="o")
    plt.title("Elbow Method — K-Means")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Inertia (within-cluster sum of squares)")
    plt.xticks(kmeans_eval["n_clusters"])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "elbow_method.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(kmeans_eval["n_clusters"], kmeans_eval["silhouette_score"], marker="o", label="K-Means")
    plt.plot(hierarchical_eval["n_clusters"], hierarchical_eval["silhouette_score"],
             marker="s", label="Hierarchical")
    plt.title("Silhouette Score Comparison")
    plt.xlabel("Number of clusters")
    plt.ylabel("Silhouette score")
    plt.xticks(range(2, max_k + 1))
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "silhouette_score.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    sample_size = min(80, len(X))
    if sample_size >= 4:
        Z = linkage(X[:sample_size], method="ward")
        dendrogram(Z, no_labels=True)
        plt.title(f"Hierarchical Clustering Dendrogram (sample of {sample_size} buyers)")
        plt.xlabel("Sampled buyers")
        plt.ylabel("Ward distance")
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / "hierarchical_dendrogram.png", dpi=160)
    plt.close()

    # K-Means cluster profile summary for the dashboard.
    buyers["cluster"] = buyers["kmeans_cluster"]
    aggregations = {
        "buyer_count": ("client_id", "nunique"),
        "avg_age": ("age", "mean"),
        "avg_properties_purchased": ("properties_purchased", "mean"),
        "avg_total_purchase_value": ("total_purchase_value", "mean"),
        "avg_property_price": ("average_property_price", "mean"),
    }
    if "satisfaction_score" in buyers.columns:
        aggregations["avg_satisfaction_score"] = ("satisfaction_score", "mean")
    summary = buyers.groupby("cluster").agg(**aggregations).reset_index()
    summary["buyer_percentage"] = summary["buyer_count"] / len(buyers) * 100
    summary.to_csv(REPORTS_DIR / "buyer_cluster_summary.csv", index=False)

    # Keep both model labels, relevant filter dimensions, and transaction metrics.
    export_cols = [
        "client_id", "cluster", "kmeans_cluster", "hierarchical_cluster",
        "client_type", "gender", "country", "region", "age", "acquisition_purpose",
        "loan_applied", "referral_channel", "satisfaction_score",
        "properties_purchased", "total_purchase_value", "average_property_price",
    ]
    export_cols = [c for c in export_cols if c in buyers.columns]
    buyers[export_cols].to_csv(REPORTS_DIR / "buyer_segments.csv", index=False)

    # Hierarchical model summary, separate from K-Means summary.
    hsummary = buyers.groupby("hierarchical_cluster").agg(
        buyer_count=("client_id", "nunique"),
        avg_age=("age", "mean"),
        avg_properties_purchased=("properties_purchased", "mean"),
        avg_total_purchase_value=("total_purchase_value", "mean"),
        avg_satisfaction_score=("satisfaction_score", "mean"),
    ).reset_index()
    hsummary["buyer_percentage"] = hsummary["buyer_count"] / len(buyers) * 100
    hsummary.to_csv(REPORTS_DIR / "hierarchical_cluster_summary.csv", index=False)

    # Simple cluster profile by major dimensions for interpretation.
    for col in ["acquisition_purpose", "country", "region", "loan_applied", "client_type"]:
        if col in buyers.columns:
            profile = pd.crosstab(buyers["cluster"], buyers[col], normalize="index").mul(100).round(2)
            profile.to_csv(REPORTS_DIR / f"cluster_by_{col}.csv")

    # Distribution chart
    plt.figure(figsize=(8, 5))
    plt.bar(summary["cluster"].astype(str), summary["buyer_count"])
    plt.title("Buyer Distribution Across K-Means Clusters")
    plt.xlabel("Cluster")
    plt.ylabel("Buyer count")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "buyer_cluster_distribution.png", dpi=160)
    plt.close()

    print("Buyer segmentation complete.")
    print(f"K-Means selected k={best_k}; Hierarchical selected k={h_best_k}.")
    print(evaluation.to_string(index=False))
    print(summary.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
