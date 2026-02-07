
import sqlite3
import csv
import os
import logging
from typing import Dict, Any
from datetime import datetime

def generate_reports(config: Dict[str, Any], logger: logging.Logger, date_str: str) -> None:
    """
    Generates summary and export reports from the database.

    Args:
        config: Configuration dictionary.
        logger: Logger instance.
        date_str: Date string for report filenames.
    """
    db_path = config.get("storage", {}).get("database_path", "data/internal_data.db")
    
    if not os.path.exists(db_path):
        logger.warning(f"Database not found at {db_path}. Skipping report generation.")
        return

    # Ensure reports directory exists
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # --- Generate Summary Report ---
            summary_file = os.path.join(reports_dir, f"summary_{date_str}.txt")
            
            # Get counts
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MAX(ingested_at) FROM market_data")
            market_last_ingested = cursor.fetchone()[0] or "Never"
            
            cursor.execute("SELECT COUNT(*) FROM news_data")
            news_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MAX(ingested_at) FROM news_data")
            news_last_ingested = cursor.fetchone()[0] or "Never"
            
            with open(summary_file, 'w') as f:
                f.write(f"Internal Data Automation Report - {date_str}\n")
                f.write("========================================\n\n")
                f.write(f"Market Data Records: {market_count}\n")
                f.write(f"Last Market Ingestion: {market_last_ingested}\n\n")
                f.write(f"News Data Records: {news_count}\n")
                f.write(f"Last News Ingestion: {news_last_ingested}\n")
            
            logger.info(f"Summary report generated at {summary_file}")

            # --- Generate Market Data CSV Export ---
            csv_file = os.path.join(reports_dir, f"market_data_{date_str}.csv")
            
            cursor.execute("SELECT * FROM market_data")
            rows = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(column_names)
                writer.writerows(rows)
                
            logger.info(f"Market data CSV exported to {csv_file}")

    except sqlite3.Error as e:
        logger.error(f"Database error during reporting: {e}")
    except IOError as e:
        logger.error(f"IO error during reporting: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during reporting: {e}")
