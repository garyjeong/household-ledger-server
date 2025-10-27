-- Household Ledger Database Initialization Script
-- This script runs automatically when the container starts for the first time
-- Note: Database and user are already created by MySQL entrypoint script

-- Use database
USE household_ledger;

-- Character set configuration
ALTER DATABASE household_ledger CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges (already done by entrypoint, but ensuring it)
-- GRANT ALL PRIVILEGES ON household_ledger.* TO 'gary'@'%';
-- FLUSH PRIVILEGES;

