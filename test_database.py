import pytest
import sqlite3
import os
import database
import time

@pytest.fixture
def db_manager(tmp_path):
    # Use valid path for DB, or mock config.DB_FILE
    # For testing, we can use a temporary file or :memory: if the class supports injection.
    # The class reads config.DB_FILE. Let's patch config.DB_FILE.
    
    d = tmp_path / "test_metrics.db"
    test_db = str(d)
    
    # Patch the config.DB_FILE in the database module scope
    original_db = database.config.DB_FILE
    database.config.DB_FILE = test_db
    
    db = database.DatabaseManager()
    yield db
    
    # Teardown - Restore config, let pytest handle file cleanup
    database.config.DB_FILE = original_db

def test_init_db(db_manager):
    assert os.path.exists(db_manager.db_file)
    with sqlite3.connect(db_manager.db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
        assert cursor.fetchone() is not None

def test_insert_and_get_metrics(db_manager):
    db_manager.insert_metric(10.0, 20.0, 30.0, 45.0)
    # Wait a tiny bit or just fetch
    # get_history fetches last 1 hour
    hist = db_manager.get_history(hours=1)
    assert len(hist) == 1
    # Check values (cpu, ram) from tuple
    # SELECT timestamp, cpu_percent, ram_percent
    assert hist[0][1] == pytest.approx(10.0)
    assert hist[0][2] == pytest.approx(20.0)

def test_audit_log(db_manager):
    db_manager.log_command(123, "/test", "SUCCESS")
    with sqlite3.connect(db_manager.db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, command FROM audit_log")
        row = cursor.fetchone()
        assert row[0] == 123
        assert row[1] == "/test"
