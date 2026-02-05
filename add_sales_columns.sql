-- sales jadvaliga yangi ustunlar (unit_price, purchase_price_at_sale, profit)
--
-- USUL 1 (tavsiya): Loyiha papasida:  python migrate_database.py
--
-- USUL 2: mysql -u root -p ngms_db < add_sales_columns.sql
-- USUL 3: MySQL klientida (Workbench, DBeaver) ushbu 3 ta ALTER TABLE ni bajarish.
-- Agar "Duplicate column name" chiqsa, o'sha ustun mavjud, keyingisiga o'ting.

ALTER TABLE sales ADD COLUMN unit_price DECIMAL(10, 2) NULL COMMENT 'Dona narxi savdo paytida';
ALTER TABLE sales ADD COLUMN purchase_price_at_sale DECIMAL(10, 2) NULL COMMENT 'Xarid narxi savdo paytida';
ALTER TABLE sales ADD COLUMN profit DECIMAL(10, 2) NULL COMMENT 'Foyda';
