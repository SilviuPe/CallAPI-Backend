# cleanup_scheduler.py
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

import psycopg2


load_dotenv('../.env')

DATABASE_HOST=os.getenv("DATABASE_HOST")
DATABASE_PORT=os.getenv("DATABASE_PORT")
DATABASE_USERNAME=os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD=os.getenv("DATABASE_PASSWORD")
DATABASE_NAME=os.getenv("DATABASE_DBNAME")


DB_DSN = os.getenv(
    "DB_DSN",
    f"dbname={DATABASE_NAME} user={DATABASE_USERNAME} password={DATABASE_PASSWORD} host={DATABASE_HOST} port={DATABASE_PORT}"
)

def cleanup_sessions():
    """Șterge sesiunile expirate; protejat cu advisory lock ca să nu ruleze dublu."""
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        # Încearcă să iei un lock global (schimbă 42 cu alt int fix dacă vrei)
        cur.execute("SELECT pg_try_advisory_lock(42);")
        locked = cur.fetchone()[0]
        if not locked:
            # Alt proces face deja cleanup
            return

        # Varianta simplă (rapidă, ai index pe expires_at)
        cur.execute("""
            DELETE FROM sessions
            WHERE expires_at <= now();
        """)
        # Dacă vrei să vezi câte rânduri s-au șters:
        # cur.rowcount are rezultate doar pentru DELETE simplu în anumite setări.
        print(f"[{datetime.utcnow().isoformat()}] Cleanup DONE.")
    except Exception as e:
        print(f"[{datetime.utcnow().isoformat()}] Cleanup ERROR: {e}")
    finally:
        # Eliberează lock-ul și conexiunea
        try:
            cur.execute("SELECT pg_advisory_unlock(42);")
        except Exception:
            pass
        cur.close()
        conn.close()

def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup_sessions, "interval", minutes=1, id="purge_sessions", max_instances=1, coalesce=True)
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to stop.")

    # Ține procesul în viață
    try:
        import time
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
    main()
