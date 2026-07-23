\# Payment Gateway NOC and Anomaly Detection Pipeline



An end-to-end data engineering and analytics solution built to simulate, detect, and isolate acquiring bank system bottlenecks and transaction outage anomalies at scale.



\---



\## Project Overview



In high-volume payment processing environments, sudden latencies or service degradation from acquiring banks can cost merchants significant revenue. 



This project simulates a 1,000,000-row synthetic transaction dataset across various Baltic and Nordic acquiring banks (Swedbank, SEB, Revolut, Siauliu Bankas, and Luminor) over a 30-day window. It injects a realistic system failure pattern—high latency and elevated timeout rates—into a specific bank node.



The primary objective was to build a complete pipeline, from relational SQL views down to an executive Network Operations Center (NOC) dashboard, capable of pinning down the exact outage source in real time.



\---



\## Tech Stack and Architecture



\* Database Engine: PostgreSQL

\* Data Generation: Python (pandas, numpy)

\* Data Modeling and Transformation: SQL (aggregations, window functions, relational views)

\* Visualization Layer: Power BI Desktop (Star Schema with custom DimDate calendar table)



\---



\## Business Problem and Key Insights



1\. Anomaly Isolation: Out of five integrated acquiring banks, Luminor experienced persistent high latency (\~800–1200ms vs. 200ms benchmark) and an elevated timeout rate (\~20%).

2\. Merchant Impact Analysis: Identified top enterprise merchants suffering the highest volume of dropped transactions during the incident window.

3\. NOC Operations: Designed a high-contrast dark theme dashboard with synchronized filtering across top-level KPIs, hourly latency trendlines, and transaction health metrics.



\---



\## Repository Structure



```text

├── 00\_init\_schema.sql        # Database schema definitions and constraints

├── 01\_initial\_discovery.sql   # Exploratory queries isolating baseline anomaly

├── 02\_outage\_analysis.sql    # Analytical queries detailing bank-level failure ratios

├── 03\_create\_views.sql       # Production-ready analytical views for BI consumption

├── generate\_shift4\_data.py   # Python synthetic dataset generator (1M rows)

├── Payment\_Gateway\_NOC.pbix  # Power BI NOC Dashboard file

└── README.md                 # Project documentation

