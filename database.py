import sqlite3
import time
import logging
import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_file = config.DB_FILE
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                # Metrics Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metrics (
                        timestamp INTEGER PRIMARY KEY,
                        cpu_percent REAL,
                        ram_percent REAL,
                        disk_percent REAL,
                        temp REAL
                    )
                ''')
                # Security Audit Log
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp INTEGER,
                        user_id INTEGER,
                        command TEXT,
                        status TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def insert_metric(self, cpu, ram, disk, temp):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO metrics (timestamp, cpu_percent, ram_percent, disk_percent, temp) VALUES (?, ?, ?, ?, ?)",
                    (int(time.time()), cpu, ram, disk, temp)
                )
                # Cleanup old metrics (keep last 48h)
                cursor.execute("DELETE FROM metrics WHERE timestamp < ?", (int(time.time()) - 172800,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to insert metric: {e}")

    def log_command(self, user_id, command, status="SUCCESS"):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO audit_log (timestamp, user_id, command, status) VALUES (?, ?, ?, ?)",
                    (int(time.time()), user_id, command, status)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to audit log: {e}")

    def get_history(self, hours=1):
        cutoff = int(time.time()) - (hours * 3600)
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT timestamp, cpu_percent, ram_percent FROM metrics WHERE timestamp > ? ORDER BY timestamp ASC",
                    (cutoff,)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
            return []
