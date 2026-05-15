# 🚀 E-Commerce End-to-End Data Pipeline

Professional Data Science project demonstrating an automated pipeline for ETL, Customer Segmentation (RFM), and Churn Prediction.

## 🛠️ Project Stack
- **Languages:** Python (Pandas, Scikit-Learn, Matplotlib).
- **Database:** SQL Server (Data ingestion).
- **Modeling:** Random Forest for Predictive Analytics.

## 📁 Repository Structure
- `scripts/`: Python modules for each pipeline stage.
- `data_sample.csv`: Lightweight version of the dataset for testing.
- `Julio_Cortez_Ecommerce_Portfolio_EN.pdf`: Full technical documentation.

> **Note:** The original dataset is +600MB. For testing purposes, please use the provided `data_sample.csv`.
>
> Business Objective: > This project solves the challenge of customer attrition in e-commerce. By integrating SQL Server data into a Python-based ML pipeline, we identify high-value customers (using RFM analysis) who are likely to churn.

Technical Highlights:



Automated ETL: Cleaned and structured +500k rows of raw transaction data.

Feature Engineering: Created behavior-based metrics like Recency, Frequency, and Monetary value.

Predictive Power: Trained a Random Forest model to predict churn with an emphasis on recall, ensuring we don't miss at-risk customers.

Scalability: Built modular scripts (.py) that can be integrated into production environments.
