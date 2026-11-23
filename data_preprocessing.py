from pathlib import Path
import pandas as pd

# Project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

# Create processed folder if it does not exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_clients():
    """Load, clean and save the client dataset."""

    file_path = DATA_DIR / "clients.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Clients file not found: {file_path}")

    df = pd.read_csv(file_path)

    # Remove accidental whitespace from column names
    df.columns = df.columns.str.strip()

    # Clean text columns without changing missing values
    text_columns = df.select_dtypes(include=["object"]).columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    # Convert date of birth into a consistent date format
    df["date_of_birth"] = pd.to_datetime(
        df["date_of_birth"],
        errors="coerce",
        format="mixed"
    )

    # Convert satisfaction score to numeric
    df["satisfaction_score"] = pd.to_numeric(
        df["satisfaction_score"],
        errors="coerce"
    )

    # Remove exact duplicate client rows, then validate that identifiers are unique.
    df = df.drop_duplicates().copy()
    if df["client_id"].duplicated().any():
        raise ValueError(
            "Conflicting rows share a client_id. Review these records before continuing."
        )

    # Handle missing buyer attributes without inventing demographic values.
    categorical_attributes = [
        "client_type", "gender", "country", "region",
        "acquisition_purpose", "loan_applied", "referral_channel"
    ]
    for column in categorical_attributes:
        if column in df.columns:
            df[column] = df[column].fillna("Unknown")

    if df["satisfaction_score"].isna().any():
        df["satisfaction_score"] = df["satisfaction_score"].fillna(
            df["satisfaction_score"].median()
        )

    # Save cleaned data
    output_path = PROCESSED_DIR / "clients_cleaned.csv"
    df.to_csv(output_path, index=False)

    print("\nCLIENT DATA CLEANING COMPLETED")
    print(f"Rows: {len(df)}")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"Saved to: {output_path}")

    return df


def clean_properties():
    """Load, clean and save the property dataset."""

    file_path = DATA_DIR / "properties.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Properties file not found: {file_path}")

    df = pd.read_csv(file_path)

    # Remove accidental whitespace from column names
    df.columns = df.columns.str.strip()

    # Clean text columns without changing missing values
    text_columns = df.select_dtypes(include=["object"]).columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    # Convert dates; unparseable dates become NaT
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce",
        format="mixed"
    )

    # Convert currency strings such as "$460,001.26" to numbers
    df["sale_price"] = pd.to_numeric(
        df["sale_price"]
        .astype("string")
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False),
        errors="coerce"
    )

    # Convert numeric columns safely
    for column in ["listing_id", "tower_number", "unit_number", "floor_area_sqft"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Remove exact duplicate property rows, then validate listing identifiers.
    df = df.drop_duplicates().copy()
    if df["listing_id"].duplicated().any():
        raise ValueError(
            "Conflicting rows share a listing_id. Review these records before continuing."
        )

    # Keep Available listings and their missing client references.
    # These records are valid and should not be deleted.

    output_path = PROCESSED_DIR / "properties_cleaned.csv"
    df.to_csv(output_path, index=False)

    print("\nPROPERTY DATA CLEANING COMPLETED")
    print(f"Rows: {len(df)}")
    print(f"Missing values by column:\n{df.isnull().sum()}")
    print(f"Saved to: {output_path}")

    return df


def main():
    print("=" * 55)
    print("REAL ESTATE DATA PREPROCESSING")
    print("=" * 55)

    clients = clean_clients()
    properties = clean_properties()

    # Check property references against the client dataset
    valid_client_ids = set(clients["client_id"].dropna())
    sold_properties = properties[
        properties["listing_status"].eq("Sold")
    ]

    unmatched_refs = (
        sold_properties["client_ref"].notna()
        & ~sold_properties["client_ref"].isin(valid_client_ids)
    ).sum()

    print("\nREFERENCE VALIDATION")
    print(f"Sold properties: {len(sold_properties)}")
    print(f"Unmatched client references among sold properties: {unmatched_refs}")

    print("\nPreprocessing finished successfully.")


if __name__ == "__main__":
    main()