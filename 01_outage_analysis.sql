SELECT 
    DATE_TRUNC('hour', timestamp_utc) AS transaction_hour,
    acquiring_bank,
    COUNT(*) AS total_txns,
    ROUND(AVG(latency_ms), 2) AS avg_latency_ms,
    COUNT(CASE WHEN status = 'Failed_Timeout' THEN 1 END) AS timeouts,
    ROUND(SUM(CASE WHEN status = 'Failed_Timeout' THEN amount_eur ELSE 0 END), 2) AS lost_revenue_eur
FROM fact_transactions
WHERE acquiring_bank = 'Luminor'
GROUP BY 1, 2
ORDER BY transaction_hour ASC;