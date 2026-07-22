-- ==========================================
-- 1. Create Dimension Table (Merchants)
-- ==========================================
CREATE TABLE public.dim_merchants (
	merchant_id varchar(50) NOT NULL,
	merchant_name varchar(255) NULL,
	municipality varchar(100) NULL,
	company_type varchar(100) NULL,
	taxes_paid_eur numeric(12, 2) NULL,
	CONSTRAINT dim_merchants_merchant_id_not_null NOT NULL merchant_id,
	CONSTRAINT dim_merchants_pkey PRIMARY KEY (merchant_id)
);

-- ==========================================
-- 2. Create Fact Table (Transactions)
-- ==========================================
CREATE TABLE public.fact_transactions (
	transaction_id bigserial NOT NULL,
	merchant_id varchar(50) NULL,
	timestamp_utc timestamp NULL,
	amount_eur numeric(10, 2) NULL,
	acquiring_bank varchar(50) NULL,
	status varchar(20) NULL,
	latency_ms int4 NULL,
	CONSTRAINT fact_transactions_pkey PRIMARY KEY (transaction_id),
	CONSTRAINT fact_transactions_transaction_id_not_null NOT NULL transaction_id
);

-- ==========================================
-- 3. Define Foreign Key Relationships
-- ==========================================
ALTER TABLE public.fact_transactions 
ADD CONSTRAINT fact_transactions_merchant_id_fkey 
FOREIGN KEY (merchant_id) REFERENCES public.dim_merchants(merchant_id);