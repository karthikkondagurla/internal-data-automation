import sqlite3

def verify_audit_logs():
    try:
        conn = sqlite3.connect("data/internal_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            print("Latest Pipeline Run:")
            print(f"Run ID: {row[0]}")
            print(f"Date: {row[1]}")
            print(f"Mode: {row[2]}")
            print(f"Status: {row[3]}")
            print(f"Started At: {row[4]}")
            print(f"Finished At: {row[5]}")
            print(f"Error Message: {row[6]}")
        else:
            print("No pipeline runs found.")
            
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    verify_audit_logs()
