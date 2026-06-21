# Author  : Neha Aidasani

import sqlite3

LOG_FILE = "bank_gateway.log"  
DB_FILE = "banking_errors.db"

def setup_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS banking_errors(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   text,
            level       text,
            service     text,
            message     text
        )
  """)
    
def parse_logs(cursor):
    errors_inserted = 0
    corrupted_found = 0

    with open(LOG_FILE, 'r') as log_file:
        for line in log_file:
            line = line.strip()
            if not line:
                continue
            
            # -- EXTRACT -- 
            parts = line.split("|")
            
            # -- TRANSFORM --

            # Corrupted line
            if len(parts) < 4:
                print(f" [Data Quality ALERT] Malformed row skipped => {line}")
                corrupted_found += 1
                continue

            timestamp, level, service, message = parts[0], parts[1], parts[2], parts[3]

            # Error only
            if level != "ERROR":
                continue

            # -- LOAD --
            cursor.execute("""
                INSERT INTO banking_errors (timestamp, level, service, message)
                VALUES(?, ?, ?, ?)
        """, (timestamp, level, service, message))
            
            errors_inserted += 1

    return errors_inserted, corrupted_found


def print_summary(cursor):
    cursor.execute("""
        SELECT service, COUNT(*) as error_count
        FROM banking_errors
        GROUP BY service
        ORDER BY error_count DESC
    """)    

    rows = cursor.fetchall()


    print("\n  =========== ERROR Report By Services ===========")
    for row in rows:
        print(f" | {row[0]:<30} | {row[1]:>4} error(s) | ")
    print("  =================================================")


def main():
    print("====================================")
    print("     Banking Log Parse Engine       ")
    print("====================================")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f" [DB] Connected to '{DB_FILE}'")
          
    setup_db(cursor)
    print(f" [DB]  Table 'banking errors' ready")
    print(f" [ENGINE] Reading '{LOG_FILE}'  \n")

    inserted, corrupted = parse_logs(cursor)

    conn.commit()

    print(f"\n [RESULT] Run Complete.")
    print(f" [RESULT] Errors inserted : {inserted}")
    print(f" [RESULT] Corrupted Skipped: {corrupted}")

    print_summary(cursor)

    conn.close()
    print(" [ENGINE] Database Connection Closed\n")


if __name__ == "__main__":
    main()