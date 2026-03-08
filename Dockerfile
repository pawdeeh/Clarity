FROM python:3.10

RUN apt-get update && apt-get install -y libpq-dev netcat-openbsd postgresql-client iputils-ping nano

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy and setup initialization scripts
COPY wait-for-it.sh /wait-for-it.sh
COPY migrate.sh /migrate.sh
COPY init-admin.py /app/init-admin.py
RUN chmod +x /wait-for-it.sh /migrate.sh

EXPOSE 8000

# Entry point: wait for DB, run migrations, create admin, then start server
ENTRYPOINT ["sh", "-c", "/migrate.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
