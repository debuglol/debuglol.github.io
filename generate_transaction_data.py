import os
import random
import unicodedata
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ==========================================
# 1. LOAD ENV VARS & DEFINE ASCII CLEANER
# ==========================================
# Load database credentials securely from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "shift4_analytics")

def remove_accents(text_val):
    """Converts non-ASCII characters (e.g., Lithuanian diacritics) to plain ASCII equivalents."""
    if not isinstance(text_val, str):
        return text_val
    normalized = unicodedata.normalize('NFD', text_val)
    return ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')

# ==========================================
# 2. CONNECT TO POSTGRESQL & WIPE TABLES
# ==========================================
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

print("INFO: Connected to PostgreSQL. Clearing existing tables...")

# Truncate tables to ensure clean state on re-runs
with engine.connect() as conn:
    conn.execute(text("TRUNCATE TABLE fact_transactions, dim_merchants RESTART IDENTITY CASCADE;"))
    conn.commit()

# ==========================================
# 3. LOAD, CLEAN & ASCII-CONVERT MERCHANTS
# ==========================================
print("INFO: Processing CSV datasets and normalizing text encoding...")

# Read datasets with automatic delimiter detection
df_taxes = pd.read_csv('taxes_paid.csv', sep=None, engine='python', dtype=str)
df_registry = pd.read_csv('merchant_registry.csv', sep=None, engine='python', dtype=str)

# Clean and extract tax sums and locations
df_taxes = df_taxes[['mm_kodas.ja_kodas', 'pavadinimas', 'savivaldybe.pavadinimas', 'suma']].dropna()
df_taxes.columns = ['merchant_id', 'merchant_name', 'municipality', 'taxes_paid_eur']
df_taxes['taxes_paid_eur'] = pd.to_numeric(df_taxes['taxes_paid_eur'], errors='coerce')

# Clean and extract company types
df_registry = df_registry[['ja_kodas', 'tipo_aprasymas']].dropna().drop_duplicates(subset=['ja_kodas'])
df_registry.columns = ['merchant_id', 'company_type']

# Convert text columns to plain ASCII
df_taxes['merchant_name'] = df_taxes['merchant_name'].apply(remove_accents)
df_taxes['municipality'] = df_taxes['municipality'].apply(remove_accents)
df_registry['company_type'] = df_registry['company_type'].apply(remove_accents)

# Merge into clean Merchant Dimension
dim_merchants = pd.merge(df_taxes, df_registry, on='merchant_id', how='inner')
dim_merchants = dim_merchants[dim_merchants['taxes_paid_eur'] > 0].drop_duplicates(subset=['merchant_id'])

# Stream merchants into PostgreSQL
dim_merchants.to_sql('dim_merchants', engine, if_exists='append', index=False, method='multi', chunksize=1000)
print(f"SUCCESS: Loaded {len(dim_merchants)} normalized merchants into dim_merchants.")

# ==========================================
# 4. GENERATE SYNTHETIC TRANSACTIONS
# ==========================================
print("INFO: Generating synthetic transaction data and simulating latency anomalies...")

acquirers = ['SEB', 'Swedbank', 'Siauliu Bankas', 'Luminor', 'Revolut']
top_merchants = dim_merchants.sort_values(by='taxes_paid_eur', ascending=False).head(500)

batch_size = 100000
total_records_needed = 1000000  # 1 Million records
current_count = 0

transactions_batch = []

while current_count < total_records_needed:
    merchant = top_merchants.sample(1).iloc[0]
    acquirer = random.choice(acquirers)
    amount = round(random.uniform(3.50, 450.00), 2)
    
    # Injected anomaly: Luminor acquiring channel experiences 20% timeout/latency spikes
    if acquirer == 'Luminor' and random.random() < 0.20:
        status = 'Failed_Timeout'
        latency_ms = random.randint(2100, 6000)
    else:
        status = 'Approved'
        latency_ms = random.randint(45, 350)
        
    transactions_batch.append({
        'merchant_id': merchant['merchant_id'],
        'timestamp_utc': datetime.now() - timedelta(minutes=random.randint(1, 43200)),
        'amount_eur': amount,
        'acquiring_bank': acquirer,
        'status': status,
        'latency_ms': latency_ms
    })
    
    current_count += 1
    
    if len(transactions_batch) >= batch_size:
        df_batch = pd.DataFrame(transactions_batch)
        df_batch.to_sql('fact_transactions', engine, if_exists='append', index=False, method='multi', chunksize=10000)
        print(f"   ... Streamed {current_count:,} / {total_records_needed:,} transactions into PostgreSQL")
        transactions_batch = []

print("SUCCESS: Data generation and database population complete.")
