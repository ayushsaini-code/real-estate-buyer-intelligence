# Real Estate Buyer Intelligence

**Data Analytics | Sales Performance | Exploratory Buyer Segmentation**

## Project Overview
This project analyses real-estate listings, completed sales, buyer profiles,
geographic patterns, financing indicators, and customer satisfaction. It
combines data preparation, exploratory data analysis, business KPIs,
K-Means and hierarchical clustering, and an interactive Streamlit dashboard.

The project is framed as a **Data Analyst project**. Clustering is a supporting
exploratory technique, not the sole purpose of the analysis.

**Important interpretation note:** The supplied dataset has no direct income
or net-worth fields. Purchase value is an observed transaction measure and
must not be treated as verified wealth, income, or affordability.

## Key Results
- 2,000 buyer records and 10,000 property listings
- 7,305 sold listings and 2,695 available listings
- Recorded sell-through rate: 73.05%
- Recorded sold-property value: $2,520,750,960.84
- Mean sold-property price: $345,072.00
- Median sold-property price: $330,997.32

The three-cluster K-Means solution is exploratory and has a modest silhouette
score. Cluster labels are arbitrary identifiers and should be interpreted
using the accompanying profile statistics.

## Dashboard Modules
1. Overview
2. Sales Analytics
3. Buyer Insights
4. Buyer Segmentation
5. Investor Behavior
6. Geographic Buyer Analysis
7. Segment Insights Panel

## Repository Structure
```text
.
├── app.py
├── styles.css
├── assets/
├── data/
│   └── README.md
├── reports/
│   ├── aggregate CSV outputs
│   └── analysis figures
├── research/
│   ├── research_paper.pdf
│   └── research_paper.md
├── src/
│   ├── data_preprocessing.py
│   ├── exploratory_analysis.py
│   ├── business_analysis.py
│   ├── buyer_segmentation.py
│   └── cluster_visualization.py
└── requirements.txt
```

## Data Privacy
Raw client and property datasets, processed client-level datasets, buyer-level
segment exports, identifier mappings, and the Tableau packaged workbook are
not included in this public GitHub-ready archive. This is intentional: the
original data and workbook may contain client-level or embedded data.

For local execution, add authorised copies of:
- `data/clients.csv`
- `data/properties.csv`

Do not commit personal information, direct identifiers, or transaction-level
data to a public repository. Keep private source data in a local folder or
private storage with appropriate access controls.

## Setup (Windows PowerShell)
Run commands from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Add the authorised source CSV files under `data/`, then run:

```powershell
python src/data_preprocessing.py
python src/exploratory_analysis.py
python src/business_analysis.py
python src/buyer_segmentation.py
python src/cluster_visualization.py
python -m streamlit run app.py
```

`app.py` expects cleaned datasets and generated reports. Run the analysis
scripts before launching the dashboard. The dashboard is not expected to run
from this public archive until the authorised local data files are supplied.

## Technology
- Python
- pandas and NumPy
- scikit-learn and SciPy
- Matplotlib and Plotly
- Streamlit
- Tableau (workbook retained separately in the private project copy)

## Research Paper
See `research/research_paper.pdf` for the formatted report and
`research/research_paper.md` for the editable Markdown version.

## Reproducibility and Limitations
- Re-run the workflow in a clean virtual environment before final submission.
- Record Python and package versions and the data execution date.
- Age is derived from date of birth at script execution; pin an explicit
  as-of date for fully reproducible future runs.
- Clustering quality depends on feature selection, encoding, scaling, and
  model choice. Evaluate cluster balance and stability, not only silhouette.
- Results describe the supplied project dataset and are not necessarily
  representative of the wider real-estate market.
