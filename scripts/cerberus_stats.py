import sqlite3
from pathlib import Path
import sys

HELP_MSG = f"""
Usage: python {sys.argv[0]} <path_to_sqlite_db>

Example:
    python {sys.argv[0]} data.db
"""

if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
    print(HELP_MSG)
    sys.exit(0)

DB_PATH = Path(sys.argv[1])
if not DB_PATH.is_file():
    print(f"[ERROR] Database file not found: {DB_PATH}")
    sys.exit(1)

class CredsDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

    def run_query(self, query, params=None):
        try:
            self.cur.execute(query, params or [])
            return self.cur.fetchone()[0]
        except Exception as e:
            print(f"[ERROR] Query failed: {e}")
            return None

    def run_query_all(self, query, params=None):
        try:
            self.cur.execute(query, params or [])
            return self.cur.fetchall()
        except Exception as e:
            print(f"[ERROR] Query failed: {e}")
            return []


    def count_total_domain_hashes(self):
        return self.run_query("SELECT COUNT(*) FROM credsdomainusers;")

    def count_unique_hashes(self):
        return self.run_query("SELECT COUNT(*) FROM credentials;")

    def count_users_with_cracked_passwords(self):
        query = """
            SELECT COUNT(*)
            FROM credsdomainusers
            INNER JOIN credentials
            ON credsdomainusers.cred_id = credentials.id
            WHERE plain IS NOT NULL;
        """
        return self.run_query(query)

    def count_users_without_cracked_passwords(self):
        query = """
            SELECT COUNT(*)
            FROM credsdomainusers
            INNER JOIN credentials
            ON credsdomainusers.cred_id = credentials.id
            WHERE plain IS NULL;
        """
        return self.run_query(query)

    def count_unique_cracked_passwords(self):
        return self.run_query("SELECT COUNT(*) FROM credentials WHERE plain IS NOT NULL;")


    def top_5_repeated_hashes(self):
        query = """
            SELECT c.ntlm, COUNT(*) AS cnt
            FROM credsdomainusers d
            JOIN credentials c ON d.cred_id = c.id
            GROUP BY d.cred_id
            ORDER BY cnt DESC
            LIMIT 5;
        """
        return self.run_query_all(query)

    def top_5_cracked_passwords(self):
        query = """
            SELECT c.plain, COUNT(*) AS cnt
            FROM credsdomainusers d
            JOIN credentials c ON d.cred_id = c.id
            WHERE c.plain IS NOT NULL
            GROUP BY d.cred_id
            ORDER BY cnt DESC
            LIMIT 5;
        """
        return self.run_query_all(query)

    def close(self):
        self.conn.close()


def main():
    db = CredsDB()

    total_hashes = db.count_total_domain_hashes()
    unique_hashes = db.count_unique_hashes()
    users_cracked = db.count_users_with_cracked_passwords()
    users_not_cracked = db.count_users_without_cracked_passwords()
    unique_cracked = db.count_unique_cracked_passwords()

    print(f"\n---- Cerberus Stats Report: {DB_PATH} ----")
    print(f"Total domain hashes:                  {total_hashes}")
    print(f"Unique hashes:                        {unique_hashes}")
    print(f"Repeated hashes:                      {total_hashes - unique_hashes}")
    if total_hashes:
        print(f"Users with cracked passwords:         {users_cracked} ({round(users_cracked / total_hashes, 2) * 100}%)")
    else:
        print(f"Users with cracked passwords:         {users_cracked}")
    print(f"Users without cracked passwords:      {users_not_cracked}")
    if unique_hashes:
        print(f"Unique cracked passwords:             {unique_cracked} ({round(unique_cracked / unique_hashes, 2) * 100}%)")
    else:
        print(f"Unique cracked passwords:             {unique_cracked}")

    print("\nTop 5 repeated hashes (uncracked):")
    for h, cnt in db.top_5_repeated_hashes():
        print(f"{h} ({cnt} times)")

    print("\nTop 5 cracked passwords:")
    for pwd, cnt in db.top_5_cracked_passwords():
        print(f"{pwd} ({cnt} times)")

    db.close()


if __name__ == "__main__":
    main()
