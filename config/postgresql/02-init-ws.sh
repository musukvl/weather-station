#!/bin/bash
set -e

# Initialize Weather Station Database
# This script is run automatically by PostgreSQL on container initialization

echo "Creating Weather Station database and user..."

# Create database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    -- Create Weather database
    SELECT 'CREATE DATABASE ${WS_DB_NAME:-weather}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${WS_DB_NAME:-weather}')\gexec

    -- Create Weather user
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${WS_DB_USER:-weather_user}') THEN
            CREATE USER ${WS_DB_USER:-weather_user} WITH PASSWORD '${WS_DB_PASSWORD:-weather_password}';
        END IF;
    END
    \$\$;

    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE ${WS_DB_NAME:-weather} TO ${WS_DB_USER:-weather_user};
EOSQL

# Connect to Weather database and grant schema permissions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname="${WS_DB_NAME:-weather}" <<-EOSQL
    GRANT ALL ON SCHEMA public TO ${WS_DB_USER:-weather_user};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${WS_DB_USER:-weather_user};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${WS_DB_USER:-weather_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${WS_DB_USER:-weather_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${WS_DB_USER:-weather_user};
EOSQL

echo "Weather Station database and user created successfully"
