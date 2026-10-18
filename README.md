# Customer Segmentation

A customer segmentation project that explores shopping patterns and groups customers using **K-Prototypes clustering**. A **Random Forest** model predicts the generated segment labels, and a **FastAPI + Gemini AI** application presents predictions with plain-language explanations.

## Project Overview

This project uses customer purchase data to explore spending patterns and identify groups that may respond to different marketing approaches.

The project has three main parts:

1. **Exploratory Data Analysis (EDA):** Power BI dashboards explore purchase amounts, product categories, seasons, subscription status, and locations.
2. **Customer Segmentation:** K-Prototypes groups customers using a mix of numerical and categorical features.
3. **Prediction App:** A Random Forest classifier predicts the cluster label, while Gemini AI helps explain the result in simple language.

## Objectives

- Explore customer purchasing patterns.
- Compare purchase amounts across categories and other available attributes.
- Group customers into three segments.
- Build an API-based interface for predicting a customer's segment.
- Present possible business actions for further testing.

## Tech Stack

- **Python**
- **Power BI** : exploratory analysis and dashboards
- **Pandas / NumPy** : data preparation and analysis
- **Scikit-learn** : preprocessing and Random Forest classification
- **K-Prototypes** : clustering mixed numerical and categorical data
- **FastAPI** : API backend
- **Gemini API** : natural-language explanations
- **HTML/CSS** : interface, if included in the repository

## Dataset

The dataset contains **3,900 records and 18 columns**, with one record per customer in the supplied data.

Fields include:

- Customer details: `CustomerID`, `Age`, `Gender`, `Location`
- Purchase details: `ItemPurchased`, `Category`, `PurchaseAmountUSD`, `Size`, `Color`
- Shopping context: `Season`, `ShippingType`, `FrequencyOfPurchases`
- Customer behaviour: `ReviewRating`, `SubscriptionStatus`, `DiscountApplied`, `PromoCodeUsed`, `PreviousPurchases`, `PaymentMethod`

The supplied dataset does not include purchase dates, product costs, profit margins, customer lifetime value, or campaign results. Therefore, the analysis describes observed patterns and does not claim to measure profitability, long-term trends, or campaign impact.

## Methodology

### 1. Exploratory Data Analysis

Power BI was used to examine the dataset and build visualizations for:

- Purchase value and average purchase amount
- Purchase value by product category
- Subscription status
- Seasonal labels in the dataset
- Customer counts by location

### 2. K-Prototypes Clustering

K-Prototypes was selected because the dataset contains both numerical and categorical features.

**Numerical features**
- `Age`
- `PurchaseAmountUSD`
- `PreviousPurchases`

**Categorical features**
- `Category`
- `SubscriptionStatus`
- `DiscountApplied`
- `PromoCodeUsed`
- `FrequencyOfPurchases`

The numerical features were scaled before clustering, and the number of clusters was set to **3**.

### 3. Random Forest Classification

The cluster labels created by K-Prototypes were used as the target for a Random Forest classifier. The classifier predicts which generated cluster a customer most closely matches.

**Important:** The reported test accuracy of **95.26%** and macro F1-score of **0.9531** measure how well the classifier reproduces the generated cluster labels. They do not independently prove that the customer segments are naturally distinct or commercially optimal.

### 4. FastAPI and Gemini AI

The application flow is:

1. Enter customer feature values in the interface.
2. Send the input to the FastAPI backend.
3. Use the trained Random Forest model to predict a cluster label.
4. Use Gemini AI to provide a plain-language explanation of the prediction.
5. Display the prediction and explanation to the user.

Gemini provides an explanation; it does not perform the K-Prototypes clustering or replace the Random Forest prediction.

## Example Findings

The following are descriptive results from this dataset:

- Total recorded purchase value: approximately **$996.38K**
- Average purchase amount: approximately **$255.48**
- Clothing had the highest total purchase value at approximately **$209K**.
- Subscription status was nearly evenly split: **49.51% Yes** and **50.49% No**.
- The K-Prototypes clusters had **1,488**, **1,220**, and **1,192** records.

The sampled Gower silhouette score was **0.0676**, suggesting weak separation between the clusters. Treat the segments as exploratory groups that may need feature refinement and further validation before being used for business decisions.

## Suggested Business Uses

These are ideas to test, not proven outcomes:

- Test product bundles for categories customers commonly purchase.
- Explore loyalty offers for customers with more previous purchases.
- Compare targeted promotions with a control group before wider rollout.
- Track conversion, repeat purchases, and profit margin to evaluate campaign performance.
- Revisit the clustering features and validation metrics if clearer segment separation is needed.

## Project Structure

Adapt this example to match the actual filenames in your repository:

```text
Customer-Segmentation/
├── app/                 # FastAPI application and interface
├── models/              # Saved preprocessing and model artifacts
├── notebooks/           # Analysis and clustering experiments, if included
├── powerbi/              # Power BI report or dashboard, if included
├── data/                 # Dataset, if permitted to share
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables (no real secrets)
├── .gitignore
└── README.md
```

## Setup

The exact commands depend on the filenames and model-loading code in your repository. A typical local setup is:

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

If your repository includes `requirements.txt`:

```bash
pip install -r requirements.txt
```

Otherwise, install the dependencies listed by your project and create a `requirements.txt` file.

### 4. Configure the Gemini API key

Create a `.env` file in the location expected by your application:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Use the variable name expected by your code if it differs. **Never commit your real API key or `.env` file to GitHub.**

### 5. Run the application

For a FastAPI app whose entry point is `app/main.py`, a typical command is:

```bash
uvicorn app.main:app --reload
```

Change the module path to match your actual project structure. Open the local URL shown in the terminal; FastAPI commonly provides interactive API documentation at `/docs`.

## Limitations

- The dataset contains one record per customer, so it does not provide a sequence of transactions over time.
- The dataset does not include costs or margins, so purchase value should not be treated as profit.
- Seasonal comparisons reflect the provided season labels, not verified time trends.
- The silhouette score indicates weak cluster separation; the segments should be treated as exploratory.
- Random Forest metrics measure agreement with the K-Prototypes-generated labels, not independent segment quality.
- Business suggestions require testing against real campaign results before drawing conclusions.


## Author

Created as part of the **CDACL-002 Customer Segmentation** project @Datamites.

---


