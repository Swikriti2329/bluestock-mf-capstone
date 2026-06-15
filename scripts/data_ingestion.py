import pandas as pd
from pathlib import Path

RAW = Path("data/raw")

DATASETS = {
    "fund_master":           "01_fund_master.csv",
    "nav_history":           "02_nav_history.csv",
    "aum_by_fund_house":     "03_aum_by_fund_house.csv",
    "monthly_sip_inflows":   "04_monthly_sip_inflows.csv",
    "category_inflows":      "05_category_inflows.csv",
    "industry_folio_count":  "06_industry_folio_count.csv",
    "scheme_performance":    "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings":    "09_portfolio_holdings.csv",
    "benchmark_indices":     "10_benchmark_indices.csv",
}

def load_all_datasets():
    dataframes = {}
    for name, filename in DATASETS.items():
        filepath = RAW / filename
        try:
            df = pd.read_csv(filepath)
            dataframes[name] = df
            print(f"\n{'='*50}")
            print(f"✅  {name.upper()}")
            print(f"    Shape  : {df.shape[0]} rows x {df.shape[1]} columns")
            print(f"    Columns: {list(df.columns)}")
            print(f"    Nulls  : {df.isnull().sum().sum()}")
            print(df.head(2).to_string())
        except FileNotFoundError:
            print(f"❌  {name}: File not found!")
    return dataframes

def validate_amfi_codes(dataframes):
    print(f"\n{'='*50}")
    print("🔍  AMFI CODE VALIDATION")
    master_codes = set(dataframes["fund_master"]["amfi_code"].astype(str))
    nav_codes    = set(dataframes["nav_history"]["amfi_code"].astype(str))
    missing = nav_codes - master_codes
    if missing:
        print(f"⚠️   Missing codes: {missing}")
    else:
        print(f"✅  All {len(nav_codes)} AMFI codes match!")

def print_fund_summary(dataframes):
    df = dataframes["fund_master"]
    print(f"\n{'='*50}")
    print("📊  FUND MASTER SUMMARY")
    for fh in sorted(df["fund_house"].unique()):
        print(f"    • {fh}")

if __name__ == "__main__":
    print("🚀  BLUESTOCK FINTECH — Day 1: Data Ingestion")
    dfs = load_all_datasets()
    validate_amfi_codes(dfs)
    print_fund_summary(dfs)
    print(f"\n✅  Total rows: {sum(df.shape[0] for df in dfs.values()):,}")
