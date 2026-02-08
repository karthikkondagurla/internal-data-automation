
import sqlite3
import os
import logging
from typing import List, Dict, Any
from datetime import datetime

class Database:
    def __init__(self, db_path: str, logger: logging.Logger):
        """
        Initialize database connection and ensure tables exist.
        
        Args:
            db_path: Path to the SQLite database file.
            logger: Logger instance.
        """
        self.db_path = db_path
        self.logger = logger
        self._ensure_db_dir()
        self._create_tables()

    def _ensure_db_dir(self):
        """Ensure the directory for the database exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection."""
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Create necessary tables if they do not exist."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                ingested_at TEXT,
                UNIQUE(date)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS news_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                published_at TEXT,
                source TEXT,
                title TEXT,
                description TEXT,
                url TEXT,
                ingested_at TEXT,
                UNIQUE(url)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                run_date TEXT,
                mode TEXT,
                status TEXT,
                started_at TEXT,
                finished_at TEXT,
                error_message TEXT
            )
            """
        ]
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for query in queries:
                    cursor.execute(query)
                conn.commit()
            self.logger.info(f"Database tables initialized at {self.db_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create tables: {e}")

    def insert_market_data(self, records: List[Dict[str, Any]]):
        """
        Insert processed market data records into the database.
        
        Args:
            records: List of market data dictionaries.
        """
        if not records:
            self.logger.info("No market records to insert.")
            return

        query = """
        INSERT OR IGNORE INTO market_data (date, open, high, low, close, volume, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        ingested_at = datetime.now().isoformat()
        data_tuples = [
            (
                r.get('date'),
                r.get('open'),
                r.get('high'),
                r.get('low'),
                r.get('close'),
                r.get('volume'),
                ingested_at
            )
            for r in records
        ]

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, data_tuples)
                conn.commit()
                self.logger.info(f"Inserted {cursor.rowcount} market records.")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to insert market data: {e}")

    def insert_news_data(self, records: List[Dict[str, Any]]):
        """
        Insert processed news data records into the database.
        
        Args:
            records: List of news data dictionaries.
        """
        if not records:
            self.logger.info("No news records to insert.")
            return

        query = """
        INSERT OR IGNORE INTO news_data (published_at, source, title, description, url, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        ingested_at = datetime.now().isoformat()
        data_tuples = [
            (
                r.get('published_at'),
                r.get('source'),
                r.get('title'),
                r.get('description'),
                r.get('url'),
                ingested_at
            )
            for r in records
        ]

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, data_tuples)
                conn.commit()
                self.logger.info(f"Inserted {cursor.rowcount} news records.")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to insert news data: {e}")

    def start_pipeline_run(self, run_id: str, run_date: str, mode: str, started_at: str):
        """记录 pipeline 开始"""
        query = """
        INSERT INTO pipeline_runs (run_id, run_date, mode, status, started_at)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(query, (run_id, run_date, mode, "STARTED", started_at))
                conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Failed to record pipeline start: {e}")

    def mark_pipeline_success(self, run_id: str, finished_at: str):
        """标记 pipeline 成功"""
        query = """
        UPDATE pipeline_runs 
        SET status = ?, finished_at = ?
        WHERE run_id = ?
        """
        try:
            with self._get_connection() as conn:
                conn.execute(query, ("SUCCESS", finished_at, run_id))
                conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Failed to record pipeline success: {e}")

    def mark_pipeline_failure(self, run_id: str, finished_at: str, error_message: str):
        """标记 pipeline 失败"""
        query = """
        UPDATE pipeline_runs 
        SET status = ?, finished_at = ?, error_message = ?
        WHERE run_id = ?
        """
        try:
            with self._get_connection() as conn:
                conn.execute(query, ("FAILED", finished_at, error_message, run_id))
                conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Failed to record pipeline failure: {e}")
