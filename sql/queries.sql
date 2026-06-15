-- Bluestock Fintech | Day 2 SQL Queries

-- Q1: Top 5 funds by latest NAV
SELECT f.scheme_name, f.fund_house, f.category,
       MAX(n.nav) as latest_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
GROUP BY n.amfi_code
ORDER BY latest_nav DESC
LIMIT 5;

-- Q2: Average NAV per month per fund house
SELECT f.fund_house,
       strftime('%Y-%m', n.date) as month,
       ROUND(AVG(n.nav), 2) as avg_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
GROUP BY f.fund_house, month
ORDER BY month DESC
LIMIT 20;

-- Q3: Top 5 funds by Sharpe Ratio
SELECT f.scheme_name, f.fund_house,
       p.sharpe_ratio, p.return_3yr_pct, p.alpha
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 5;

-- Q4: Total SIP amount by state
SELECT state,
       COUNT(*) as num_transactions,
       ROUND(SUM(amount_inr)/1000000.0, 2) as total_sip_lakhs
FROM fact_transactions
WHERE transaction_type = 'Sip'
GROUP BY state
ORDER BY total_sip_lakhs DESC;

-- Q5: Funds with expense ratio below 1%
SELECT scheme_name, fund_house, category, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- Q6: SIP inflow growth year over year
SELECT strftime('%Y', month) as year,
       ROUND(SUM(sip_inflow_crore), 2) as total_sip_crore
FROM fact_sip
GROUP BY year
ORDER BY year;

-- Q7: Transaction split by type
SELECT transaction_type,
       COUNT(*) as count,
       ROUND(SUM(amount_inr)/10000000.0, 2) as total_crore
FROM fact_transactions
GROUP BY transaction_type;

-- Q8: Top sectors in portfolio holdings
SELECT sector,
       ROUND(AVG(weight_pct), 2) as avg_weight,
       COUNT(*) as num_holdings
FROM fact_portfolio
GROUP BY sector
ORDER BY avg_weight DESC
LIMIT 10;

-- Q9: Funds with highest max drawdown (most risky)
SELECT f.scheme_name, f.category,
       p.max_drawdown_pct, p.beta
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.max_drawdown_pct ASC
LIMIT 5;

-- Q10: AUM growth by fund house 2022 to 2025
SELECT fund_house,
       ROUND(MAX(aum_crore)/100000.0, 2) as peak_aum_lakh_crore
FROM fact_aum
GROUP BY fund_house
ORDER BY peak_aum_lakh_crore DESC;
