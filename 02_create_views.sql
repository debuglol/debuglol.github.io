-- View 1: Hourly Bank Performance Metrics
CREATE OR REPLACE VIEW vw_hourly_bank_health AS
SELECT 
    DATE_TRUNC('hour', timestamp_utc) AS transaction_hour,
    acquiring_bank,
    COUNT(*) AS total_txns,
    ROUND(AVG(latency_ms), 2) AS avg_latency_ms,
    COUNT(CASE WHEN status = 'Failed_Timeout' THEN 1 END) AS timeouts,
    ROUND(
        COUNT(CASE WHEN status = 'Failed_Timeout' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS failure_rate_pct,
    ROUND(SUM(CASE WHEN status = 'Failed_Timeout' THEN amount_eur ELSE 0 END), 2) AS lost_revenue_eur,
    ROUND(SUM(CASE WHEN status = 'Approved' THEN amount_eur ELSE 0 END), 2) AS approved_revenue_eur
FROM fact_transactions
GROUP BY 1, 2;

-- View 2: Smart Routing Revenue Recovery Summary
CREATE OR REPLACE VIEW vw_smart_routing_summary AS
SELECT 
    acquiring_bank,
    COUNT(*) AS total_transactions,
    COUNT(CASE WHEN status = 'Approved' THEN 1 END) AS actual_approved_txns,
    COUNT(CASE WHEN status = 'Failed_Timeout' THEN 1 END) AS actual_failed_txns,
    ROUND(SUM(CASE WHEN status = 'Approved' THEN amount_eur ELSE 0 END), 2) AS actual_approved_revenue_eur,
    ROUND(SUM(CASE WHEN status = 'Failed_Timeout' THEN amount_eur ELSE 0 END), 2) AS revenue_at_risk_eur,
    -- Smart routing salvage calculation (99% recovery rate on failover)
    ROUND(SUM(CASE WHEN status = 'Failed_Timeout' THEN amount_eur ELSE 0 END) * 0.99, 2) AS salvaged_revenue_eur
FROM fact_transactions
GROUP BY acquiring_bank;