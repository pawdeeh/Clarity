#!/bin/sh

# Wait for the database to be ready
/wait-for-it.sh db:5432 --timeout=120 --strict

# Check if alembic/versions folder exists and has no migration files
if [ ! -d "alembic/versions" ] || [ -z "$(ls -A alembic/versions)" ]; then
  echo "No migrations found, generating new migration..."
  alembic revision --autogenerate -m "Auto migration"
  alembic upgrade head
else
  echo "Migrations are already generated. Upgrading to latest..."
  alembic upgrade head
fi

# Initialize admin user if needed
echo "Initializing admin account..."
python /app/init-admin.py
