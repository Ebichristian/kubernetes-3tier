import os
import time
from dotenv import load_dotenv
import threading
import psycopg2
from flask import Flask

app = Flask(__name__)

def load_env():
    load_dotenv()
    env_vars = {
        "APP_NAME": os.getenv("APP_NAME"),
        "DATABASE_URL": os.getenv("DATABASE_URL")
    }
    return env_vars

def check_db_connection(db_url):
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        return True
    except Exception:
        return False

def log_env_and_db():
    while True:
        env = load_env()
        print(f"[ENV] APP_NAME={env['APP_NAME']}, DATABASE_URL={env['DATABASE_URL']}")
        
        db_status = check_db_connection(env['DATABASE_URL'])
        print("[DB STATUS]", "connected" if db_status else "not connected")

        time.sleep(1)

@app.route("/")
def index():
    return "Flask App Running..."

if __name__ == "__main__":
    threading.Thread(target=log_env_and_db, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
