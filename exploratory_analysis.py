from pathlib import Path

import pandas as pd

# Project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

CLIENTS_PATH = DATA_DIR / "clients.csv"
PROPERTIES_PATH = DATA_DIR / "properties.csv"


def analyze_dataset(file_path, dataset_name):
    """Display a basic quality and statistical report."""

    print("\n" + "=" * 65)
    print(f"DATASET: {dataset_name}")
    print("=" * 65)

    # Check whether the file exists
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return None

    # Load dataset
    df = pd.read_csv(file_path)

    # 1. Dataset dimensions
    print("\n1. DATASET DIMENSIONS")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    # 2. Column names
    print("\n2. COLUMN NAMES")
    print(df.columns.tolist())

    # 3. Data types
    print("\n3. DATA TYPES")
    print(df.dtypes.to_string())

    # 4. Missing values
    print("\n4. MISSING VALUES")
    missing = pd.DataFrame({
        "Missing Count": df.isnull().sum(),
        "Missing Percentage": (
            df.isnull().mean() * 100
        ).round(2)
    })

    print(missing.to_string())

    # 5. Duplicate records
    print("\n5. DUPLICATE RECORDS")
    print(f"Duplicate rows: {df.duplicated().sum()}")

    # 6. Descriptive statistics
    print("\n6. NUMERICAL SUMMARY")
    print(df.describe().to_string())

    # 7. Categorical summaries
    print("\n7. CATEGORICAL SUMMARY")

    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns

    for column in categorical_columns:
        print(f"\n{column}:")
        print(df[column].value_counts(dropna=False).head(10))

    return df


def main():
    clients_df = analyze_dataset(
        CLIENTS_PATH,
        "CLIENTS DATA"
    )

    properties_df = analyze_dataset(
        PROPERTIES_PATH,
        "PROPERTIES DATA"
    )

    if clients_df is not None and properties_df is not None:
        print("\n" + "=" * 65)
        print("INITIAL DATA ANALYSIS COMPLETED")
        print("=" * 65)


if __name__ == "__main__":
    main()