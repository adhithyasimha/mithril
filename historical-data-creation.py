import pymysql
import pandas as pd
import random
import string
from faker import Faker

# ---------- DB ----------
DB_HOST = "mithril-case-database.ctogioe46r4p.us-west-2.rds.amazonaws.com"
DB_USER = "admin"
DB_PASS = "Qwerty123$"
DB_NAME = "mithril-case-database"
DB_PORT = 3306

# ---------- FILE ----------
CSV_PATH = "fedex_ar_snapshot_6900.csv"
BASE_EMAIL = "psadhithya03@gmail.com"

fake = Faker()

# ---------- SQL ----------
INSERT_QUERY = """
INSERT INTO customer (
    customer_id,
    customer_name,
    business_segment,
    tin_number,
    phone_number,
    email
)
VALUES (%s, %s, %s, %s, %s, %s);
"""

# ---------- GENERATORS ----------
def generate_unique_tin(existing):
    """
    Format: lzhpa8589a
    (5 letters + 4 digits + 1 letter) = 10 chars
    """
    while True:
        tin = (
            "".join(random.choices(string.ascii_lowercase, k=5)) +
            "".join(random.choices(string.digits, k=4)) +
            random.choice(string.ascii_lowercase)
        )
        if tin not in existing:
            existing.add(tin)
            return tin

def generate_unique_email(existing):
    while True:
        alias = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        email = f"psadhithya03+{alias}@gmail.com"
        if email not in existing:
            existing.add(email)
            return email

# ---------- MAIN ----------
def main():
    # Load CSV
    df = pd.read_csv(CSV_PATH)


    df = df.drop_duplicates(subset=["customer_id"])

    # Connect DB
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT
    )
    cursor = conn.cursor()

    used_tins = set()
    used_emails = set()
    used_phones = set()

    records = []

    for _, row in df.iterrows():
        # Unique phone (10 digits)
        phone = fake.unique.msisdn()[:10]

        tin = generate_unique_tin(used_tins)
        email = generate_unique_email(used_emails)

        records.append((
            row["customer_id"],
            row["customer_name"],
            row["business_segment"],
            tin,
            phone,
            email
        ))

    cursor.executemany(INSERT_QUERY, records)
    conn.commit()

    cursor.close()
    conn.close()

    print(f"SUCCESS: Inserted {len(records)} unique customers")

if __name__ == "__main__":
    main()
