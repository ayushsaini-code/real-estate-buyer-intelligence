from pathlib import Path
import pandas as pd

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR = PROJECT_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    """Load the cleaned datasets."""

    clients_path = PROCESSED_DIR / "clients_cleaned.csv"
    properties_path = PROCESSED_DIR / "properties_cleaned.csv"

    if not clients_path.exists() or not properties_path.exists():
        raise FileNotFoundError(
            "Cleaned datasets not found. Run data_preprocessing.py first."
        )

    clients = pd.read_csv(clients_path)
    properties = pd.read_csv(properties_path)

    # Parse dates after reading CSV files
    clients["date_of_birth"] = pd.to_datetime(
        clients["date_of_birth"], errors="coerce", format="mixed"
    )
    properties["transaction_date"] = pd.to_datetime(
        properties["transaction_date"], errors="coerce", format="mixed"
    )

    properties["sale_price"] = pd.to_numeric(
        properties["sale_price"], errors="coerce"
    )

    return clients, properties


def analyze_business(clients, properties):
    """Calculate business KPIs and explore buyer/property patterns."""

    sold = properties[
        properties["listing_status"].eq("Sold")
    ].copy()

    available = properties[
        properties["listing_status"].eq("Available")
    ].copy()

    # Sales KPIs use Sold properties only.
    # Available listings are not counted as completed sales.
    total_sales_value = sold["sale_price"].sum()
    average_sale_price = sold["sale_price"].mean()
    median_sale_price = sold["sale_price"].median()

    total_properties = len(properties)
    sold_count = len(sold)
    available_count = len(available)

    sold_percentage = (
        sold_count / total_properties * 100
        if total_properties else 0
    )

    # Buyer profile
    buyer_purpose = clients["acquisition_purpose"].value_counts()
    client_types = clients["client_type"].value_counts()
    loan_counts = clients["loan_applied"].value_counts()
    referral_counts = clients["referral_channel"].value_counts()
    satisfaction_counts = clients["satisfaction_score"].value_counts().sort_index()

    # Property breakdowns
    property_categories = properties["unit_category"].value_counts()
    sold_categories = sold["unit_category"].value_counts()

    # Regional distribution
    region_counts = clients["region"].value_counts().head(10)
    country_counts = clients["country"].value_counts().head(10)

    # Monthly sold-property metrics
    sold["transaction_month"] = (
        sold["transaction_date"].dt.to_period("M").astype("string")
    )

    monthly_sales = (
        sold.groupby("transaction_month", dropna=False)
        .agg(
            properties_sold=("listing_id", "count"),
            sales_value=("sale_price", "sum"),
            average_sale_price=("sale_price", "mean")
        )
        .reset_index()
    )

    # Merge sold properties with clients to explore buyer behavior.
    # Left join preserves every sold property even if a reference is missing.
    buyer_sales = sold.merge(
        clients,
        left_on="client_ref",
        right_on="client_id",
        how="left",
        validate="many_to_one"
    )

    purpose_sales = (
        buyer_sales.groupby("acquisition_purpose", dropna=False)
        .agg(
            properties_sold=("listing_id", "count"),
            sales_value=("sale_price", "sum"),
            average_sale_price=("sale_price", "mean")
        )
        .reset_index()
    )

    # Print KPIs
    print("\n" + "=" * 60)
    print("REAL ESTATE BUSINESS ANALYSIS")
    print("=" * 60)

    print("\n1. PROPERTY KPIs")
    print(f"Total property listings: {total_properties:,}")
    print(f"Properties sold: {sold_count:,}")
    print(f"Properties available: {available_count:,}")
    print(f"Sold percentage: {sold_percentage:.2f}%")
    print(f"Total recorded sales value: ${total_sales_value:,.2f}")
    print(f"Average sold property price: ${average_sale_price:,.2f}")
    print(f"Median sold property price: ${median_sale_price:,.2f}")

    print("\n2. CLIENT PROFILE")
    print(f"Total clients: {len(clients):,}")
    print("\nAcquisition purpose:")
    print(buyer_purpose.to_string())
    print("\nClient type:")
    print(client_types.to_string())
    print("\nLoan application:")
    print(loan_counts.to_string())

    print("\n3. REFERRAL CHANNELS")
    print(referral_counts.to_string())

    print("\n4. CUSTOMER SATISFACTION")
    print(satisfaction_counts.to_string())

    print("\n5. PROPERTY CATEGORY")
    print("\nAll listings:")
    print(property_categories.to_string())
    print("\nSold listings:")
    print(sold_categories.to_string())

    print("\n6. TOP 10 REGIONS BY CLIENT COUNT")
    print(region_counts.to_string())

    print("\n7. TOP 10 COUNTRIES BY CLIENT COUNT")
    print(country_counts.to_string())

    print("\n8. MONTHLY SALES")
    print(monthly_sales.to_string(index=False))

    print("\n9. SALES BY BUYER PURPOSE")
    print(purpose_sales.to_string(index=False))

    # Save analysis tables for Tableau and further work.
    buyer_purpose.rename_axis("acquisition_purpose").reset_index(
        name="client_count"
    ).to_csv(OUTPUT_DIR / "buyer_purpose.csv", index=False)

    referral_counts.rename_axis("referral_channel").reset_index(
        name="client_count"
    ).to_csv(OUTPUT_DIR / "referral_channels.csv", index=False)

    satisfaction_counts.rename_axis("satisfaction_score").reset_index(
        name="client_count"
    ).to_csv(OUTPUT_DIR / "customer_satisfaction.csv", index=False)

    property_categories.rename_axis("unit_category").reset_index(
        name="listing_count"
    ).to_csv(OUTPUT_DIR / "property_categories.csv", index=False)

    region_counts.rename_axis("region").reset_index(
        name="client_count"
    ).to_csv(OUTPUT_DIR / "top_regions.csv", index=False)

    monthly_sales.to_csv(OUTPUT_DIR / "monthly_sales.csv", index=False)
    purpose_sales.to_csv(OUTPUT_DIR / "sales_by_buyer_purpose.csv", index=False)

    print(f"\nAnalysis tables saved in: {OUTPUT_DIR}")
    print("Business analysis completed successfully.")


def main():
    clients, properties = load_data()
    analyze_business(clients, properties)


if __name__ == "__main__":
    main()