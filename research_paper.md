# Real Estate Buyer Intelligence
## Data Analytics, Sales Performance and Exploratory Buyer Segmentation

**Research Paper | Data Analyst Internship Project**  
**Dataset period:** January 2024 - December 2025  
**Report date:** 23 November 2026

> This report documents the analysis and implementation evidenced by the supplied project files. It distinguishes measured dataset results from exploratory model outputs and recommendations.

## Abstract
This project develops a data-analytics workflow for examining real-estate listings, completed sales, buyer profiles, and buyer-level purchase behaviour. The supplied datasets contain 2,000 clients and 10,000 property records. The workflow includes data cleaning, identifier and reference validation, descriptive and business analysis, monthly sales reporting, buyer-level feature aggregation, exploratory clustering, and interactive dashboard delivery.

The property dataset contains 7,305 sold listings and 2,695 available listings. Sold listings represent 73.05% of all records and have a combined recorded sale value of $2,520,750,960.84. The mean sold-property price is $345,072.00 and the median is $330,997.32. All 7,305 sold-property client references match supplied client identifiers.

For exploratory segmentation, the implementation derives age and buyer-level transaction features, applies One-Hot Encoding to categorical attributes and StandardScaler to numeric attributes, and evaluates K-Means and Ward-linkage hierarchical clustering. The current evaluation report records the highest K-Means silhouette score at k=3 (0.124087). Hierarchical clustering records 0.470688 at k=2, but yields a highly imbalanced split of 1,963 and 37 buyers. The dashboard presents the three-group K-Means profile as its primary segmentation view, while retaining hierarchical clustering as a comparison. The modest K-Means score indicates substantial overlap and supports cautious interpretation.

The project is delivered through a multi-page Streamlit application and a Tableau workbook. The data contains no income or net-worth variables; purchase value is treated only as observed transaction behaviour, not as a proxy for wealth.

## 1. Introduction
The project analyses property inventory, sales, buyer characteristics, financing indicators, acquisition purpose, satisfaction, and geography. It is framed as a Data Analyst internship project, with clustering used as a supporting exploratory technique.

## 2. Problem Definition, Aim and Objectives
**Problem:** The supplied client and property records require cleaning, integration, summarisation, and presentation before they can support structured business review.  
**Aim:** Build a data-driven real-estate buyer intelligence workflow that analyses property sales and buyer behaviour, explores buyer segments, and communicates findings through dashboards.  
**Objectives:** inspect data quality; clean and validate records; calculate sales KPIs; summarise buyer profiles; aggregate buyer-level transaction features; compare clustering candidates; and publish findings through Streamlit and Tableau.

## 3. Background and Literature Review
Descriptive analytics establishes the scale and composition of historical records. Unsupervised segmentation groups observations based on selected attributes and depends on feature selection, encoding, scaling, and algorithm choice. K-Means minimises within-cluster squared distances; Ward-linkage hierarchical clustering merges groups to minimise increases in within-cluster variance. Silhouette analysis measures cohesion and separation but should be considered alongside cluster balance, stability, and interpretability.

## 4. Dataset Description and Data Governance
- `clients.csv`: 2,000 records, 12 fields.
- `properties.csv`: 10,000 records, 9 fields.
- Client fields include client type, date of birth, gender, country, region, acquisition purpose, satisfaction, loan application, and referral channel.
- Property fields include transaction date, category, floor area, sale price, listing status, and client reference.
- Dataset provenance and sampling frame are not documented in the supplied archive; results describe this dataset only.
- Names and dates of birth are present in the client file and should not be exposed in public reporting.

## 5. Research Design and Methodology
The workflow inspects raw data, cleans and validates records, calculates business KPIs, aggregates sold transactions to buyer level, encodes and scales features, evaluates clustering models, exports reports, and presents outputs in dashboards. It is quantitative and observational; no causal or experimental design is implemented.

## 6. Data Preparation and Quality Assurance
Text whitespace is stripped; dates and prices are parsed; exact duplicate rows are removed; client and listing identifiers are checked for uniqueness. Missing categorical client attributes are labelled `Unknown`; missing satisfaction values, if any, are median-imputed. Available listings retain missing `client_ref` values. In the inspected processed data, clients have zero missing values, properties have 2,695 missing `client_ref` values, there are no duplicate rows, and all 7,305 sold references match client IDs.

## 7. Exploratory Data Analysis
| Indicator | Result |
|---|---:|
| Total listings | 10,000 |
| Sold listings | 7,305 |
| Available listings | 2,695 |
| Sell-through rate | 73.05% |
| Recorded sold-property value | $2,520,750,960.84 |
| Mean sold-property price | $345,072.00 |
| Median sold-property price | $330,997.32 |

Buyer profile counts: Home 1,385; Investment 615; Individual 1,897; Company 103; Loan No 1,264; Loan Yes 736; Website referral 1,103; Agency 705; Client referral 192. Satisfaction counts are score 1=395, 2=379, 3=404, 4=417, 5=405. Property categories are Apartment 8,547 and Office 1,453. USA accounts for 1,538 clients; the largest regions include California (633), Nevada (143), Colorado (118), Arizona (108), and Oregon (96).

## 8. Feature Engineering and Buyer-Level Aggregation
Sold properties with valid client references and positive sale prices are grouped by client reference to derive: number of properties purchased, total purchase value, and average property price. Age is derived from date of birth at script execution. The resulting matched population contains 2,000 buyers.

Categorical features: client_type, gender, country, region, acquisition_purpose, loan_applied, referral_channel.  
Numeric features: age, satisfaction_score, properties_purchased, total_purchase_value, average_property_price.  
One-Hot Encoding is used for nominal categories; StandardScaler is applied to numeric features. LabelEncoder mappings are exported for traceability only and are not used as nominal distance features.

## 9. Model Development and Evaluation
K-Means is evaluated for k=2 through 8 with `random_state=42` and `n_init=10`. Its highest silhouette score is at k=3: 0.124087. Agglomerative hierarchical clustering uses Ward linkage; its highest score is at k=2: 0.470688. However, hierarchical k=2 produces 1,963 buyers (98.15%) and 37 buyers (1.85%). The dashboard uses K-Means k=3 as its primary segmentation view; this is a practical three-profile choice, not proof that K-Means is superior overall.

| Model | k | Silhouette |
|---|---:|---:|
| K-Means | 2 | 0.123916 |
| K-Means | 3 | 0.124087 |
| K-Means | 4 | 0.107086 |
| K-Means | 5 | 0.097321 |
| K-Means | 6 | 0.093006 |
| K-Means | 7 | 0.091961 |
| K-Means | 8 | 0.089155 |
| Hierarchical | 2 | 0.470688 |
| Hierarchical | 3 | 0.111056 |
| Hierarchical | 4 | 0.068445 |
| Hierarchical | 5 | 0.056056 |
| Hierarchical | 6 | 0.050134 |
| Hierarchical | 7 | 0.047601 |
| Hierarchical | 8 | 0.046614 |

## 10. Results and Interpretation
| Cluster | Buyers | Share | Avg. age | Avg. properties | Avg. total purchase value | Avg. property price | Avg. satisfaction |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 51 | 2.55% | 65.16 | 7.29 | $2,397,660 | $330,963 | 3.49 |
| 1 | 898 | 44.90% | 55.12 | 3.66 | $1,465,877 | $404,867 | 3.17 |
| 2 | 1,051 | 52.55% | 57.14 | 3.47 | $1,029,603 | $298,506 | 2.89 |

Cluster 0 is a small group with the highest mean property count and total recorded purchase value. Cluster 1 has the highest average property price. Cluster 2 is the largest group and has the lowest average satisfaction. These are descriptive differences, not verified wealth classifications. The K-Means silhouette score is modest, indicating substantial overlap.

## 11. Dashboard and System Implementation
The Streamlit app includes Overview, Sales Analytics, Buyer Insights, Buyer Segmentation, Investor Behavior, Geographic Buyer Analysis, and Segment Insights Panel. Filters include country, region, acquisition purpose, and client type. The app uses a dark emerald/gold CSS theme. Geographic analysis uses country/region summaries and a USA state choropleth when region names map to US states; the source data has no latitude/longitude. The archive also includes `Real_Estate_Market_Intelligence.twbx`.

## 12. Discussion
The project links descriptive business reporting with exploratory segmentation. The K-Means solution is modestly separated, while the higher hierarchical k=2 silhouette corresponds to a highly imbalanced split. Model choice should consider cluster balance, stability, interpretability, and business validation rather than one metric alone.

## 13. Business Recommendations
1. Investigate Cluster 0's higher recorded multi-purchase activity; do not label it as wealthy.
2. Examine Cluster 1's higher average property price alongside property category, area, region, and acquisition purpose.
3. Prioritise satisfaction research for Cluster 2, the largest group with the lowest mean satisfaction.
4. Track referral-channel conversion and transaction outcomes before changing acquisition budgets.
5. Report geographic sample sizes alongside regional comparisons.
6. Validate segments across time periods and with business stakeholders before operational use.

## 14. Limitations, Ethics and Responsible Use
No income or net-worth fields are available. The source provenance and sampling frame are not documented. The dataset is geographically concentrated. Age changes with execution date. Cluster separation is weak for K-Means, and hierarchical k=2 is imbalanced. Purchase value must not be treated as income or net worth. Clusters should not determine credit, housing access, or other high-impact decisions. Direct identifiers should be removed from public releases.

## 15. Conclusion and Future Work
The project provides a reproducible workflow for cleaning and analysing the supplied real-estate records, calculating sales indicators, deriving buyer-level features, evaluating clustering methods, and communicating findings through Streamlit and Tableau. Future work should document data provenance, pin the age calculation date, test cluster stability and temporal validity, compare alternative mixed-data methods, add validated data fields only where lawful and ethical, and implement automated data-quality and KPI tests.

## References
- MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability, 1, 281-297.
- Lloyd, S. P. (1982). Least squares quantization in PCM. IEEE Transactions on Information Theory, 28(2), 129-137.
- Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. Journal of Computational and Applied Mathematics, 20, 53-65.
- Ward, J. H., Jr. (1963). Hierarchical grouping to optimize an objective function. Journal of the American Statistical Association, 58(301), 236-244.
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825-2830.
- McKinney, W. (2010). Data structures for statistical computing in Python. Proceedings of the 9th Python in Science Conference, 56-61.
- Streamlit documentation: https://docs.streamlit.io/
- Plotly Python documentation: https://plotly.com/python/
- Tableau Help: https://help.tableau.com/

## Appendix A. Reproducibility
From the project root, create a fresh environment, install `requirements.txt`, then run:
```powershell
python src/data_preprocessing.py
python src/exploratory_analysis.py
python src/business_analysis.py
python src/buyer_segmentation.py
python src/cluster_visualization.py
python -m streamlit run app.py
```

## Appendix B. Metric Definitions
- Sell-through rate = sold listings / all listings x 100.
- Total recorded sales value = sum of sale_price for Sold listings only.
- Average sold price = mean sale_price for Sold listings only.
- Properties purchased = distinct sold listing count grouped by client_ref.
- Total purchase value = sum of sold sale_price grouped by client_ref.
- Average property price = mean sold sale_price grouped by client_ref.
- Buyer share = cluster buyer_count / matched buyers x 100.
