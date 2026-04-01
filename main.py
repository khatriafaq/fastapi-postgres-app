import os
import time
import psycopg2
from fastapi import FastAPI

app = FastAPI()

# ── Database connection with retry ──────────────────────
def get_connection():
    for attempt in range(5):          # try up to 5 times
        try:
            return psycopg2.connect(
                host=os.getenv('DB_HOST', 'db'),
                dbname=os.getenv('DB_NAME', 'appdb'),
                user=os.getenv('DB_USER', 'devops'),
                password=os.getenv('DB_PASSWORD', 'secret123')
            )
        except psycopg2.OperationalError:
            print(f'DB not ready (attempt {attempt+1}/5), waiting 2s...')
            time.sleep(2)
    raise RuntimeError('Cannot connect to database after 5 attempts')

# ── Routes ──────────────────────────────────────────────
@app.get('/')
def home():
    return {'message': 'Hello from FastAPI!', 'status': 'ok'}

@app.get('/db-check')
def db_check():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute('SELECT version();')
    version = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {'postgres_version': version}
