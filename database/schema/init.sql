-- =============================================================================
-- File:    database/schema/init.sql
-- Purpose: Personal budget tracking schema (MySQL 8.0)
--
-- Design goals:
--   1. Dependent category → subcategory lists (enforced by FK)
--   2. Credit-card purchases tracked for budgeting WITHOUT distorting cash balance
--   3. Fixed (planned monthly) vs Extra (unplanned) spending tagged on every row
--   4. Month-over-month comparison via views
--   5. Loan / lend-money lifecycle tracked end-to-end
--
-- Tables (in FK order):
--   accounts · categories · subcategories · monthly_plans · monthly_plan_items · transactions
-- Views:
--   v_account_cash_balance · v_monthly_expense_summary · v_credit_outstanding · v_budget_vs_actual
-- =============================================================================
CREATE DATABASE IF NOT EXISTS finance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE finance_db;
-- ============================================================
-- 1. ACCOUNTS
--    Track each bank account or credit card separately.
--    account_type controls how balances are calculated in views.
-- ============================================================
CREATE TABLE IF NOT EXISTS accounts (
  account_id INT NOT NULL AUTO_INCREMENT,
  account_name VARCHAR(100) NOT NULL,
  account_type ENUM('savings', 'expense', 'credit') NOT NULL,
  -- savings  → SC Bank, receives salary; source for monthly transfer
  -- expense  → ACB bank day-to-day spending account
  -- credit   → SC credit card(s); balance = what you still owe
  currency VARCHAR(3) NOT NULL DEFAULT 'VND',
  note VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (account_id)
);
-- ============================================================
-- 2. CATEGORIES
--    Top-level groupings. category_type drives UI logic and view filters.
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
  category_id INT NOT NULL AUTO_INCREMENT,
  category_name VARCHAR(100) NOT NULL,
  category_type ENUM('expense', 'income', 'transfer', 'debt') NOT NULL,
  -- expense  → money spent (food, transport, entertainment …)
  -- income   → money received (salary, gifts …)
  -- transfer → internal move between your own accounts (no net worth change)
  -- debt     → loans you give or receive; tracked until repaid
  color_hex VARCHAR(7),
  -- e.g. '#7b68ee' — used by Streamlit / Power BI
  sort_order TINYINT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (category_id),
  UNIQUE KEY uq_category_name (category_name)
);
-- ============================================================
-- 3. SUBCATEGORIES
--    Always linked to a single parent category.
--    A frontend SELECT for subcategory should filter by category_id
--    — this replaces managing two independent flat lists.
-- ============================================================
CREATE TABLE IF NOT EXISTS subcategories (
  subcategory_id INT NOT NULL AUTO_INCREMENT,
  category_id INT NOT NULL,
  subcategory_name VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (subcategory_id),
  UNIQUE KEY uq_cat_sub (category_id, subcategory_name),
  FOREIGN KEY (category_id) REFERENCES categories (category_id)
);
-- ============================================================
-- 4. MONTHLY PLANS
--    Record your planned budget at the start of each month.
--    fixed_budget = the amount you transfer to your expense account.
--    Compare actual fixed/extra spend against this to see overruns.
-- ============================================================
CREATE TABLE IF NOT EXISTS monthly_plans (
  plan_id INT NOT NULL AUTO_INCREMENT,
  plan_year SMALLINT NOT NULL,
  plan_month TINYINT NOT NULL,
  fixed_budget DECIMAL(15, 0) NOT NULL DEFAULT 0,
  -- total you plan to transfer to expense account this month
  savings_target DECIMAL(15, 0) NOT NULL DEFAULT 0,
  -- how much you intend to keep untouched in savings
  note TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (plan_id),
  UNIQUE KEY uq_plan_ym (plan_year, plan_month),
  CONSTRAINT chk_month CHECK (
    plan_month BETWEEN 1 AND 12
  )
);
-- ============================================================
-- 5. MONTHLY PLAN ITEMS
--    Budget breakdown per category for each monthly plan.
--    One row per category per month — sum of budgeted = monthly_plans.fixed_budget.
--    Used to compare planned vs actual spend per category.
-- ============================================================
CREATE TABLE IF NOT EXISTS monthly_plan_items (
  item_id INT NOT NULL AUTO_INCREMENT,
  plan_id INT NOT NULL,
  category_id INT NOT NULL,
  budgeted DECIMAL(15, 0) NOT NULL DEFAULT 0,
  note VARCHAR(255),
  PRIMARY KEY (item_id),
  UNIQUE KEY uq_plan_category (plan_id, category_id),
  FOREIGN KEY (plan_id) REFERENCES monthly_plans (plan_id),
  FOREIGN KEY (category_id) REFERENCES categories (category_id)
);
-- ============================================================
-- 6. TRANSACTIONS  (single source of truth for every money event)
--
--  transaction_type  — what kind of movement is this?
--  spending_type     — was this within your fixed monthly budget or extra?
--  payment_method    — how was the money moved?
--
--  CREDIT CARD LOGIC:
--    When you buy on credit  → transaction_type = 'credit_purchase'
--      ✓ Counts toward your category spend for that month
--      ✗ Does NOT reduce your cash balance (no real money left your account yet)
--    When you pay credit bill → transaction_type = 'credit_payment'
--      ✓ Reduces your cash balance
--      ✗ NOT counted as an expense (already captured above — avoids double-count)
--    v_credit_outstanding shows: total purchased − total paid = what you still owe
--
--  LOAN LOGIC:
--    loan_given          → you lend to someone (cash out, creates receivable)
--    loan_received       → you borrow (cash in, creates payable)
--    loan_repayment_in   → someone pays you back
--    loan_repayment_out  → you pay back what you owe
--    related_transaction_id links a repayment back to the original loan row.
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
  transaction_id INT NOT NULL AUTO_INCREMENT,
  transaction_date DATE NOT NULL,
  account_id INT NOT NULL,
  plan_id INT,
  -- links to monthly_plans; NULL for transfers/loans
  category_id INT,
  subcategory_id INT,
  -- Allowed values for transaction_type:
  --   income           = salary, mom gives you money, any inflow
  --   expense          = cash / momo spend
  --   transfer_out     = move money out of THIS account (savings -> expense account)
  --   transfer_in      = receive a transfer INTO this account
  --   credit_purchase  = buy with credit card; counts for budget but NOT cash yet
  --   credit_payment   = pay off credit card bill; real cash impact only
  --   loan_given       = you lend money to someone
  --   loan_received    = you borrow money
  --   loan_repayment_in  = someone pays you back
  --   loan_repayment_out = you repay a debt
  transaction_type ENUM(
    'income',
    'expense',
    'transfer_out',
    'transfer_in',
    'credit_purchase',
    'credit_payment',
    'loan_given',
    'loan_received',
    'loan_repayment_in',
    'loan_repayment_out'
  ) NOT NULL,
  -- fixed = within your planned monthly budget
  -- extra = unplanned; pulled from savings
  -- NULL  = not applicable (income, transfers, loans)
  spending_type ENUM('fixed', 'extra'),
  amount DECIMAL(15, 0) NOT NULL,
  -- always positive; VND has no decimals
  payment_method ENUM('cash', 'bank_transfer', 'credit_card', 'momo'),
  note TEXT,
  related_transaction_id INT,
  -- credit_payment -> credit_purchase; loan repayment -> original loan
  is_regretted BOOLEAN NOT NULL DEFAULT FALSE,
  source_data VARCHAR(10) NOT NULL DEFAULT 'nodejs',
  -- mark impulse/wasteful spends
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (transaction_id),
  FOREIGN KEY (account_id) REFERENCES accounts (account_id),
  FOREIGN KEY (plan_id) REFERENCES monthly_plans (plan_id),
  FOREIGN KEY (category_id) REFERENCES categories (category_id),
  FOREIGN KEY (subcategory_id) REFERENCES subcategories (subcategory_id),
  FOREIGN KEY (related_transaction_id) REFERENCES transactions (transaction_id),
  CONSTRAINT chk_amount_positive CHECK (amount > 0),
  CONSTRAINT chk_source_data CHECK (source_data IN ('nodejs', 'python')),
  UNIQUE KEY uq_transaction (transaction_date, account_id, transaction_type, spending_type, amount, payment_method, note(200))
);
CREATE INDEX idx_tx_date ON transactions (transaction_date);
CREATE INDEX idx_tx_type ON transactions (transaction_type);
CREATE INDEX idx_tx_spending ON transactions (spending_type);
CREATE INDEX idx_tx_cat ON transactions (category_id, subcategory_id);
-- ============================================================
-- VIEWS
-- ============================================================
-- ── A: Real cash balance per account ────────────────────────
-- credit_purchase is intentionally excluded (no cash impact).
-- credit_payment IS included (real money left your account).
CREATE OR REPLACE VIEW v_account_cash_balance AS
SELECT a.account_id,
  a.account_name,
  a.account_type,
  COALESCE(
    SUM(
      CASE
        WHEN t.transaction_type IN (
          'income',
          'transfer_in',
          'loan_received',
          'loan_repayment_in'
        ) THEN t.amount
        WHEN t.transaction_type IN (
          'expense',
          'transfer_out',
          'credit_payment',
          'loan_given',
          'loan_repayment_out'
        ) THEN - t.amount
        ELSE 0 -- credit_purchase: no cash movement
      END
    ),
    0
  ) AS cash_balance
FROM accounts a
  LEFT JOIN transactions t ON a.account_id = t.account_id
GROUP BY a.account_id,
  a.account_name,
  a.account_type;
-- ── B: Monthly expense summary (for month-over-month analysis) ──
-- Uses credit_purchase date = when you actually spent.
-- Excludes credit_payment to avoid double-counting.
CREATE OR REPLACE VIEW v_monthly_expense_summary AS
SELECT YEAR(t.transaction_date) AS yr,
  MONTH(t.transaction_date) AS mo,
  c.category_name,
  c.category_type,
  s.subcategory_name,
  t.spending_type,
  -- fixed vs extra breakdown
  COUNT(*) AS tx_count,
  SUM(t.amount) AS total_amount
FROM transactions t
  LEFT JOIN categories c ON t.category_id = c.category_id
  LEFT JOIN subcategories s ON t.subcategory_id = s.subcategory_id
WHERE t.transaction_type IN ('expense', 'credit_purchase')
GROUP BY 1,
  2,
  3,
  4,
  5,
  6;
-- ── C: Credit card outstanding balance ──────────────────────
CREATE OR REPLACE VIEW v_credit_outstanding AS
SELECT a.account_id,
  a.account_name,
  SUM(
    CASE
      WHEN t.transaction_type = 'credit_purchase' THEN t.amount
      ELSE 0
    END
  ) AS total_purchased,
  SUM(
    CASE
      WHEN t.transaction_type = 'credit_payment' THEN t.amount
      ELSE 0
    END
  ) AS total_paid,
  SUM(
    CASE
      WHEN t.transaction_type = 'credit_purchase' THEN t.amount
      WHEN t.transaction_type = 'credit_payment' THEN - t.amount
      ELSE 0
    END
  ) AS outstanding
FROM accounts a
  LEFT JOIN transactions t ON a.account_id = t.account_id
WHERE a.account_type = 'credit'
GROUP BY a.account_id,
  a.account_name;
-- ── D: Budget vs Actual per category per month ───────────────
-- Joins monthly_plan_items (what you planned) with actual transactions.
-- remaining > 0 = under budget; remaining < 0 = over budget.
CREATE OR REPLACE VIEW v_budget_vs_actual AS
SELECT mp.plan_year AS yr,
  mp.plan_month AS mo,
  c.category_name,
  mpi.budgeted,
  COALESCE(SUM(t.amount), 0) AS actual_spent,
  mpi.budgeted - COALESCE(SUM(t.amount), 0) AS remaining
FROM monthly_plan_items mpi
  JOIN monthly_plans mp ON mpi.plan_id = mp.plan_id
  JOIN categories c ON mpi.category_id = c.category_id
  LEFT JOIN transactions t ON t.plan_id = mp.plan_id
  AND t.category_id = mpi.category_id
  AND t.transaction_type IN ('expense', 'credit_purchase')
GROUP BY mp.plan_year,
  mp.plan_month,
  c.category_name,
  mpi.budgeted;
-- ============================================================
-- SEED DATA  — accounts, categories, subcategories
-- ============================================================
INSERT INTO accounts (account_name, account_type, note)
VALUES (
    'savings (SC Bank)',
    'savings',
    'Receives salary; source for monthly transfer'
  ),
  (
    'expense (ACB)',
    'expense',
    'Day-to-day spending; funded at start of month'
  ),
  (
    'credit (SC Credit)',
    'credit',
    'Pay later; track via credit_purchase / credit_payment'
  );
INSERT INTO categories (
    category_name,
    category_type,
    color_hex,
    sort_order
  )
VALUES ('Food & Drinks', 'expense', '#a855f7', 1),
  -- daily meals, coffee, snacks, eating out
  ('Housing & Bills', 'expense', '#f87171', 2),
  -- rent, electricity, water, internet — mostly fixed
  ('Transportation', 'expense', '#facc15', 3),
  -- fuel, grab, parking
  ('Personal Care', 'expense', '#dc2626', 4),
  -- gym, haircut, medicine
  ('Entertainment', 'expense', '#4ade80', 5),
  -- movies, hobbies, games
  ('Education', 'expense', '#713f12', 6),
  -- tuition, courses, books
  ('Shopping', 'expense', '#fb923c', 7),
  -- clothes, electronics, household items
  ('Dating', 'expense', '#f9a8d4', 8),
  -- dinner, gifts, activities with partner
  ('Family', 'expense', '#93c5fd', 9),
  -- mom allowance, family gifts (replaces Give Mom)
  ('Miscellaneous', 'expense', '#d1d5db', 10),
  -- last resort; note required in app
  ('Debt', 'debt', '#166534', 11),
  -- lend out + borrow + repayments
  ('Savings & Investing', 'transfer', '#6d28d9', 12),
  -- internal transfers to savings
  ('Income', 'income', '#1d4ed8', 13);
-- salary, freelance, any inflow
-- Food & Drinks
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Daily meals' name
    UNION ALL
    SELECT 'Eating out'
    UNION ALL
    SELECT 'Coffee/Drinks'
    UNION ALL
    SELECT 'Snacks'
  ) s
WHERE category_name = 'Food & Drinks';
-- Housing & Bills
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Rent' name
    UNION ALL
    SELECT 'Electricity'
    UNION ALL
    SELECT 'Water'
    UNION ALL
    SELECT 'Internet/Phone'
    UNION ALL
    SELECT 'Others'
  ) s
WHERE category_name = 'Housing & Bills';
-- Transportation
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Fuel' name
    UNION ALL
    SELECT 'Grab/Taxi'
    UNION ALL
    SELECT 'Parking'
    UNION ALL
    SELECT 'Others'
  ) s
WHERE category_name = 'Transportation';
-- Personal Care
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Gym Membership' name
    UNION ALL
    SELECT 'Haircut'
    UNION ALL
    SELECT 'Medicine'
    UNION ALL
    SELECT 'Others'
  ) s
WHERE category_name = 'Personal Care';
-- Entertainment
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Movies' name
    UNION ALL
    SELECT 'Hobbies'
    UNION ALL
    SELECT 'Badminton'
    UNION ALL
    SELECT 'Games'
    UNION ALL
    SELECT 'Others'
  ) s
WHERE category_name = 'Entertainment';
-- Education
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Tuition' name
    UNION ALL
    SELECT 'Courses'
    UNION ALL
    SELECT 'Books'
    UNION ALL
    SELECT 'Degree'
  ) s
WHERE category_name = 'Education';
-- Shopping
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Clothes' name
    UNION ALL
    SELECT 'Electronics'
    UNION ALL
    SELECT 'Others'
  ) s
WHERE category_name = 'Shopping';
-- Dating
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Dinner' name
    UNION ALL
    SELECT 'Gifts'
    UNION ALL
    SELECT 'Activities'
    UNION ALL
    SELECT 'Others'
  ) s
WHERE category_name = 'Dating';
-- Family
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Mom Allowance' name
    UNION ALL
    SELECT 'Family Extra'
    UNION ALL
    SELECT 'Others'
  ) s
WHERE category_name = 'Family';
-- Miscellaneous (catch-all — enforce note in app when this is selected)
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  'Others'
FROM categories
WHERE category_name = 'Miscellaneous';
-- Debt (lend, borrow, all repayments in one category)
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Lend to Friends' name
    UNION ALL
    SELECT 'Borrow from Others'
    UNION ALL
    SELECT 'Repay (Momo)'
    UNION ALL
    SELECT 'Repay (Bank)'
    UNION ALL
    SELECT 'Credit Card Bill'
    UNION ALL
    SELECT 'Others'
  ) s
WHERE category_name = 'Debt';
-- Savings & Investing
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Emergency Fund' name
    UNION ALL
    SELECT 'Stocks'
    UNION ALL
    SELECT 'Monthly Transfer'
  ) s
WHERE category_name = 'Savings & Investing';
-- Income
INSERT INTO subcategories (category_id, subcategory_name)
SELECT category_id,
  s.name
FROM categories,
  (
    SELECT 'Salary' name
    UNION ALL
    SELECT 'Freelance'
    UNION ALL
    SELECT 'From Mom'
    UNION ALL
    SELECT 'Others'
  ) s
WHERE category_name = 'Income';