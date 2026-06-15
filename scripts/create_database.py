"""
Day 2 - SQLite Database Creation
Bluestock Fintech Mutual Fund Analytics Capstone
"""

import pandas as pd
import sqlite3
from pathlib import Path

PROCESSED = Path("data/processed")
DB_PATH = Path("data/db/bluestock_mf.db")
DB_PATH.parent.mkdir(exist_ok=True)

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS dim_fund;
    DROP TABLE IF EXISTS fact_nav;
    DROP TABLE IF EXISTS fact_transactions;
    DROP TABLE IF EXISTS fact_performance;
    DROP TABLE IF EXISTS fact_aum;
    DROP TABLE IF EXISTS fact_sip;
    DROP TABLE IF EXISTS fact_portfolio;
    DROP TABLE IF EXISTS fact_benchmark;

    CREATE TABLE dim_fund (
        amfi_code TEXT PRIMARY KEY,
        fund_house TEXT,
        scheme_name TEXT,
        category TEXT,
        sub_category TEXT,
        plan TEXT,
        benchmark TEXT,
        expense_ratio_pct REAL,
        risk_category TEXT,
        fund_manager TEXT
    );

    CREATE TABLE fact_nav (
        amfi_code TEXT,
        date TEXT,
        nav REAL,
        daily_return_pct REAL,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );

    CREATE TABLE fact_transactions (
        investor_id TEXT,
        transaction_date TEXT,
        amfi_code TEXT,
        transaction_type TEXT,
        amount_inr INTEGER,
        state TEXT,
        city TEXT,
        city_tier TEXT,
        age_group TEXT,
        gender TEXT,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );

    CREATE TABLE fact_performance (
        amfi_code TEXT,
        return_1yr_pct REAL,
        return_3yr_pct REAL,
        return_5yr_pct REAL,
        alpha REAL,
        beta REAL,
        sharpe_ratio REAL,
        sortino_ratio REAL,
        max_drawdown_pct REAL,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );

    CREATE TABLE fact_aum (
        fund_house TEXT,
        date TEXT,
        aum_crore REAL
    );

    CREATE TABLE fact_sip (
        month TEXT,
        sip_inflow_crore REAL,
        active_sip_accounts_crore REAL
    );

    CREATE TABLE fact_portfolio (
        amfi_code TEXT,
        stock_symbol TEXT,
        stock_name TEXT,
        sector TEXT,
        weight_pct REAL
    );

    CREATE TABLE fact_benchmark (
        date TEXT,
        index_name TEXT,
        close_value REAL
    );

    CREATE INDEX idx_nav_code ON fact_nav(amfi_code);
    CREATE INDEX idx_nav_date ON fact_nav(date);
    CREATE INDEX idx_tx_code ON fact_transactions(amfi_code);
    CREATE INDEX idx_tx_date ON fact_transactions(transaction_date);
    """)

    print("✅ Tables created successfully!")

    # Load data
    print("\n📥 Loading data into database...")

    df = pd.read_csv(PROCESSED / "clean_fund_master.csv")
    df[["amfi_code","fund_house","scheme_name","category","sub_category",
        "plan","benchmark","expense_ratio_pct","risk_category","fund_manager"]]\
        .to_sql("dim_fund", conn, if_exists="append", index=False)
    print(f"   ✅ dim_fund: {len(df)} rows")

    df = pd.read_csv(PROCESSED / "clean_nav_history.csv")
    df[["amfi_code","date","nav","daily_return_pct"]]\
        .to_sql("fact_nav", conn, if_exists="append", index=False)
    print(f"   ✅ fact_nav: {len(df):,} rows")

    df = pd.read_csv(PROCESSED / "clean_transactions.csv")
    df[["investor_id","transaction_date","amfi_code","transaction_type",
        "amount_inr","state","city","city_tier","age_group","gender"]]\
        .to_sql("fact_transactions", conn, if_exists="append", index=False)
    print(f"   ✅ fact_transactions: {len(df):,} rows")

    df = pd.read_csv(PROCESSED / "clean_performance.csv")
    df[["amfi_code","return_1yr_pct","return_3yr_pct","return_5yr_pct",
        "alpha","beta","sharpe_ratio","sortino_ratio","max_drawdown_pct"]]\
        .to_sql("fact_performance", conn, if_exists="append", index=False)
    print(f"   ✅ fact_performance: {len(df)} rows")

    df = pd.read_csv(PROCESSED / "clean_aum.csv")
    df.to_sql("fact_aum", conn, if_exists="append", index=False)
    print(f"   ✅ fact_aum: {len(df)} rows")

    df = pd.read_csv(PROCESSED / "clean_sip_inflows.csv")
    df.to_sql("fact_sip", conn, if_exists="append", index=False)
    print(f"   ✅ fact_sip: {len(df)} rows")

    df = pd.read_csv(PROCESSED / "clean_portfolio_holdings.csv")
    df.to_sql("fact_portfolio", conn, if_exists="append", index=False)
    print(f"   ✅ fact_portfolio: {len(df)} rows")

    df = pd.read_csv(PROCESSED / "clean_benchmark_indices.csv")
    df.to_sql("fact_benchmark", conn, if_exists="append", index=False)
    print(f"   ✅ fact_benchmark: {len(df):,} rows")

    conn.commit()
    conn.close()
    print(f"\n✅ Database created at {DB_PATH}")

if __name__ == "__main__":
    print("🚀 BLUESTOCK FINTECH — Day 2: Database Creation")
    print("="*50)
    create_database()
