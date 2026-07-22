-- Initial Discovery: Aggregate bank performance to find bottlenecks
SELECT 
    acquiring_bank,
    COUNT(*) AS total_transactions,
    ROUND(AVG(latency_ms), 2) AS avg_latency_ms,
    COUNT(CASE WHEN status = 'Failed_Timeout' THEN 1 END) AS total_timeouts,
    ROUND(
        COUNT(CASE WHEN status = 'Failed_Timeout' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS failure_rate_pct
FROM fact_transactions
GROUP BY acquiring_bank
ORDER BY avg_latency_ms DESC;