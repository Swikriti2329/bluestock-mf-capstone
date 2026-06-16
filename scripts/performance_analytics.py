"""
Day 4 - Fund Performance Analytics
Bluestock Fintech Mutual Fund Analytics Capstone
Compute Sharpe, Alpha, Beta, CAGR, and Fund Scorecard
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

PROCESSED = Path("data/processed")
OUTPUTS = Path("data/processed")

print("🚀 BLUESTOCK FINTECH — Day 4: Performance Analytics")
print("="*60)

# ── Load Data ──────────────────────────────────────────────────────────────
df_nav = pd.read_csv(PROCESSED / "clean_nav_history.csv", parse_dates=["date"])
df_fund = pd.read_csv(PROCESSED / "clean_fund_master.csv")
df_bench = pd.read_csv(PROCESSED / "clean_benchmark_indices.csv")

df_nav = df_nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)
df_bench["date"] = pd.to_datetime(df_bench["date"])
df_bench = df_bench.sort_values("date")

# ── Helper Functions ───────────────────────────────────────────────────────
def compute_cagr(start_price, end_price, years):
    """Compound Annual Growth Rate"""
    if start_price <= 0 or end_price <= 0:
        return 0
    return (pow(end_price / start_price, 1 / years) - 1) * 100

def compute_sharpe(returns, rf=6.5):
    """Sharpe Ratio with 6.5% risk-free rate"""
    if len(returns) == 0 or returns.std() == 0:
        return 0
    annual_return = returns.mean() * 252
    annual_std = returns.std() * np.sqrt(252)
    return (annual_return - rf) / annual_std if annual_std > 0 else 0

def compute_sortino(returns, rf=6.5):
    """Sortino Ratio - penalizes downside only"""
    if len(returns) == 0:
        return 0
    annual_return = returns.mean() * 252
    downside = returns[returns < 0].std() * np.sqrt(252)
    return (annual_return - rf) / downside if downside > 0 else 0

def compute_max_drawdown(prices):
    """Maximum peak-to-trough decline"""
    if len(prices) == 0:
        return 0
    running_max = prices.cummax()
    drawdown = (prices - running_max) / running_max
    return drawdown.min() * 100

# ── 1. COMPUTE DAILY RETURNS ───────────────────────────────────────────────
print("\n📊 Computing daily returns...")
df_nav["daily_return"] = df_nav.groupby("amfi_code")["nav"].pct_change()
df_nav["daily_return_pct"] = df_nav["daily_return"] * 100

# ── 2. COMPUTE CAGR ────────────────────────────────────────────────────────
print("📊 Computing CAGR...")
cagr_results = []

for code in df_nav["amfi_code"].unique():
    fund_data = df_nav[df_nav["amfi_code"] == code].sort_values("date")
    if len(fund_data) < 2:
        continue
    
    start_date = fund_data["date"].min()
    end_date = fund_data["date"].max()
    start_nav = fund_data["nav"].iloc[0]
    end_nav = fund_data["nav"].iloc[-1]
    
    years_total = (end_date - start_date).days / 365.25
    
    # 1-year CAGR
    one_year_ago = end_date - pd.Timedelta(days=365)
    data_1yr = fund_data[fund_data["date"] >= one_year_ago]
    cagr_1yr = compute_cagr(data_1yr["nav"].iloc[0], end_nav, 1) if len(data_1yr) > 1 else 0
    
    # 3-year CAGR
    three_years_ago = end_date - pd.Timedelta(days=365*3)
    data_3yr = fund_data[fund_data["date"] >= three_years_ago]
    cagr_3yr = compute_cagr(data_3yr["nav"].iloc[0], end_nav, 3) if len(data_3yr) > 1 else 0
    
    # 5-year CAGR
    five_years_ago = end_date - pd.Timedelta(days=365*5)
    data_5yr = fund_data[fund_data["date"] >= five_years_ago]
    cagr_5yr = compute_cagr(data_5yr["nav"].iloc[0], end_nav, 5) if len(data_5yr) > 1 else 0
    
    # Overall CAGR
    cagr_overall = compute_cagr(start_nav, end_nav, years_total)
    
    cagr_results.append({
        "amfi_code": code,
        "return_1yr_pct": cagr_1yr,
        "return_3yr_pct": cagr_3yr,
        "return_5yr_pct": cagr_5yr,
        "return_overall_pct": cagr_overall,
    })

df_cagr = pd.DataFrame(cagr_results)
print(f"   ✅ CAGR computed for {len(df_cagr)} funds")

# ── 3. COMPUTE SHARPE & SORTINO ────────────────────────────────────────────
print("📊 Computing Sharpe & Sortino Ratios...")
risk_results = []

for code in df_nav["amfi_code"].unique():
    fund_returns = df_nav[df_nav["amfi_code"] == code]["daily_return"].dropna()
    if len(fund_returns) < 30:
        continue
    
    sharpe = compute_sharpe(fund_returns)
    sortino = compute_sortino(fund_returns)
    std_dev = fund_returns.std() * np.sqrt(252) * 100
    
    fund_data = df_nav[df_nav["amfi_code"] == code].sort_values("date")
    max_dd = compute_max_drawdown(fund_data["nav"].values)
    
    risk_results.append({
        "amfi_code": code,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "std_dev_ann_pct": std_dev,
        "max_drawdown_pct": max_dd,
    })

df_risk = pd.DataFrame(risk_results)
print(f"   ✅ Risk metrics computed for {len(df_risk)} funds")

# ── 4. COMPUTE ALPHA & BETA ────────────────────────────────────────────────
print("📊 Computing Alpha & Beta vs Nifty 100...")
alpha_beta_results = []

# Get Nifty 100 returns
nifty_data = df_bench[df_bench["index_name"] == "NIFTY50"].sort_values("date").copy()
nifty_data["nifty_return"] = nifty_data["close_value"].pct_change()

for code in df_nav["amfi_code"].unique()[:10]:  # Top 10 for speed
    fund_data = df_nav[df_nav["amfi_code"] == code].sort_values("date").copy()
    
    # Merge fund returns with benchmark
    merged = fund_data.merge(nifty_data[["date","nifty_return"]], on="date")
    merged = merged.dropna()
    
    if len(merged) < 30:
        continue
    
    # Regress fund returns on benchmark returns
    X = merged["nifty_return"].values
    y = merged["daily_return"].values
    
    if X.std() > 0:
        slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
        beta = slope
        alpha = (intercept * 252) * 100  # Annualized
    else:
        beta = 0
        alpha = 0
    
    alpha_beta_results.append({
        "amfi_code": code,
        "alpha": alpha,
        "beta": beta,
        "r_squared": r_value**2,
    })

df_alpha_beta = pd.DataFrame(alpha_beta_results)
print(f"   ✅ Alpha & Beta computed for {len(df_alpha_beta)} funds")

# ── 5. MERGE ALL METRICS ───────────────────────────────────────────────────
print("📊 Merging all metrics...")
df_performance = df_cagr.merge(df_risk, on="amfi_code", how="left")
df_performance = df_performance.merge(df_alpha_beta, on="amfi_code", how="left")
df_performance = df_performance.merge(df_fund[["amfi_code","scheme_name","fund_house",
                                                "category","expense_ratio_pct"]], 
                                      on="amfi_code", how="left")

# ── 6. BUILD FUND SCORECARD ────────────────────────────────────────────────
print("📊 Building Fund Scorecard...")

def rank_and_scale(series, ascending=False, weight=1.0):
    """Rank series and scale 0-100"""
    ranked = series.rank(ascending=ascending, na_option='bottom')
    scaled = (ranked / len(ranked)) * 100 * weight
    return scaled.fillna(0)

df_performance["return_rank"] = rank_and_scale(df_performance["return_3yr_pct"], ascending=False, weight=0.30)
df_performance["sharpe_rank"] = rank_and_scale(df_performance["sharpe_ratio"], ascending=False, weight=0.25)
df_performance["alpha_rank"] = rank_and_scale(df_performance["alpha"].fillna(0), ascending=False, weight=0.20)
df_performance["expense_rank"] = rank_and_scale(df_performance["expense_ratio_pct"], ascending=True, weight=0.15)
df_performance["dd_rank"] = rank_and_scale(df_performance["max_drawdown_pct"].abs(), ascending=True, weight=0.10)

df_performance["fund_score"] = (df_performance["return_rank"] + 
                                df_performance["sharpe_rank"] + 
                                df_performance["alpha_rank"] + 
                                df_performance["expense_rank"] + 
                                df_performance["dd_rank"])

df_performance = df_performance.sort_values("fund_score", ascending=False)

# ── 7. SAVE RESULTS ────────────────────────────────────────────────────────
print("📊 Saving results...")
df_performance.to_csv(OUTPUTS / "fund_scorecard.csv", index=False)
df_cagr.to_csv(OUTPUTS / "cagr_report.csv", index=False)
df_risk.to_csv(OUTPUTS / "risk_metrics.csv", index=False)

# ── 8. PRINT SUMMARY ───────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("📊 TOP 10 FUNDS BY SCORECARD")
print(f"{'='*60}")
top_10 = df_performance[["scheme_name","fund_house","category","return_3yr_pct",
                         "sharpe_ratio","expense_ratio_pct","fund_score"]].head(10)
for idx, row in top_10.iterrows():
    print(f"\n{row['scheme_name'][:40]}")
    print(f"  Fund House: {row['fund_house']}")
    print(f"  3yr Return: {row['return_3yr_pct']:.2f}% | Sharpe: {row['sharpe_ratio']:.2f} | Expense: {row['expense_ratio_pct']:.2f}%")
    print(f"  SCORE: {row['fund_score']:.1f}/100")

print(f"\n{'='*60}")
print(f"✅ Performance analytics complete!")
print(f"   Fund Scorecard: {OUTPUTS / 'fund_scorecard.csv'}")
print(f"   CAGR Report: {OUTPUTS / 'cagr_report.csv'}")
print(f"   Risk Metrics: {OUTPUTS / 'risk_metrics.csv'}")
