#!/bin/bash
set -e

# Grant permissions on Weather Station tables
# This runs after schema creation

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname="${WS_DB_NAME:-weather}" <<-EOSQL
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${WS_DB_USER:-weather_user};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${WS_DB_USER:-weather_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${WS_DB_USER:-weather_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${WS_DB_USER:-weather_user};
EOSQL

echo "Weather Station permissions granted"
