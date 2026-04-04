-- =============================================================================
-- File: database/schema/init.sql
-- Purpose: MySQL DDL to initialise the finance_db database and all core tables.
--          Run once when the database container starts (or manually via MySQL CLI).
--          Tables: categories, merchants, expenses (fact table), time_dim.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS finance_db;
USE finance_db;

CREATE TABLE IF NOT EXISTS categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  parent_category VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS merchants (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  category_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS expenses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  expense_date DATE NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(10) DEFAULT 'USD',
  description VARCHAR(500),
  merchant_id INT,
  category_id INT NOT NULL,
  payment_method VARCHAR(50),
  notes TEXT,
  needs_cleaning BOOLEAN DEFAULT FALSE,
  source VARCHAR(50) DEFAULT 'python-api',
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (merchant_id) REFERENCES merchants(id),
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS time_dim (
  date_key DATE PRIMARY KEY,
  day INT,
  month INT,
  month_name VARCHAR(20),
  quarter INT,
  year INT,
  day_of_week VARCHAR(20),
  is_weekend BOOLEAN
);
