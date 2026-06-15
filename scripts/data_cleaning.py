"""
Day 2 - Data Cleaning Script
Bluestock Fintech Mutual Fund Analytics Capstone
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(exist_ok=True)

# ── 1. Clean NAV History ───────────────────────────────────────────────────
def clean_nav_history():
    print("\n📊 Cleaning NAV History...")
    df = pd.read_csv(RAW / "02_nav_history.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["amfi_code", "date"])
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df[df["nav"] > 0]
    full_dates = pd.date_range(df["date"].min(), df["date"].max(), freq="B")
    cleaned = []
    for code, group in df.groupby("amfi_code"):
        group = group.set_index("date").reindex(full_dates)
        group["amfi_code"] = code
        group["nav"] = group["nav"].ffill()
        group = group.reset_index().rename(columns={"index": "date"})
        cleaned.append(group)
    df_clean = pd.concat(cleaned)
    df_clean["daily_return_pct"] = df_clean.groupby("amfi_code")["nav"].pct_change() * 100
    df_clean.to_csv(PROCESSED / "clean_nav_history.csv", index=False)
    print(f"   ✅ NAV History: {len(df_clean):,} rows saved")
    return df_clean

# ── 2. Clean Fund Master ───────────────────────────────────────────────────
def clean_fund_master():
    print("\n📊 Cleaning Fund Master...")
    df = pd.read_csv(RAW / "01_fund_master.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.drop_duplicates(subset=["amfi_code"])
    df["expense_ratio_pct"] = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
    df.to_csv(PROCESSED / "clean_fund_master.csv", index=False)
    print(f"   ✅ Fund Master: {len(df)} rows saved")
    return df

# ── 3. Clean Investor Transactions ────────────────────────────────────────
def clean_transactions():
    print("\n📊 Cleaning Investor Transactions...")
    df = pd.read_csv(RAW / "08_investor_transactions.csv")
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["transaction_type"] = df["transaction_type"].str.strip().str.title()
    df = df[df["amount_inr"] > 0]
    df = df.drop_duplicates()
    df.to_csv(PROCESSED / "clean_transactions.csv", index=False)
    print(f"   ✅ Transactions: {len(df):,} rows saved")
    return df

# ── 4. Clean Scheme Performance ───────────────────────────────────────────
def clean_performance():
    print("\n📊 Cleaning Scheme Performance...")
    df = pd.read_csv(RAW / "07_scheme_performance.csv")
    numeric_cols = ["return_1yr_pct","return_3yr_pct","return_5yr_pct",
                    "alpha","beta","sharpe_ratio","sortino_ratio",
                    "std_dev_ann_pct","max_drawdown_pct"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df.to_csv(PROCESSED / "clean_performance.csv", index=False)
    print(f"   ✅ Performance: {len(df)} rows saved")
    return df

# ── 5. Clean remaining datasets ───────────────────────────────────────────
def clean_others():
    files = {
        "03_aum_by_fund_house.csv":   "clean_aum.csv",
        "04_monthly_sip_inflows.csv": "clean_sip_inflows.csv",
        "05_category_inflows.csv":    "clean_category_inflows.csv",
        "06_industry_folio_count.csv":"clean_folio_count.csv",
        "09_portfolio_holdings.csv":  "clean_portfolio_holdings.csv",
        "10_benchmark_indices.csv":   "clean_benchmark_indices.csv",
    }
    for raw_file, clean_file in files.items():
        df = pd.read_csv(RAW / raw_file)
        df = df.drop_duplicates()
        df.to_csv(PROCESSED / clean_file, index=False)
        print(f"   ✅ {clean_file}: {len(df)} rows saved")

if __name__ == "__main__":
    print("🚀 BLUESTOCK FINTECH — Day 2: Data Cleaning")
    print("="*50)
    clean_nav_history()
    clean_fund_master()
    clean_transactions()
    clean_performance()
    print("\n📊 Cleaning remaining datasets...")
    clean_others()
    print("\n✅ All datasets cleaned and saved to data/processed/")
