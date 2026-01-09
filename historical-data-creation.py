import pandas as pd
import pymysql
import random

CSV_PATH = "dataset-vol-6900.csv"

DB_HOST = "mithril-case-database.ctogioe46r4p.us-west-2.rds.amazonaws.com"
DB_USER = "admin"
DB_PASS = "Qwerty123$"
DB_NAME = "mithril-case-database"
DB_PORT = 3306

# ---------- Load CSV ----------
df = pd.read_csv(CSV_PATH)

# ---------- Clean ----------
df["customer_id"] = df["customer_id"].astype(str).str.strip()
df["customer_name"] = df["customer_name"].astype(str).str.strip()
df["business_segment"] = df["business_segment"].astype(str).str.strip().str.lower()

df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")

# ---------- Segment ranges ----------
TOTAL_RANGES = {
    "small": (25, 150),
    "mid": (180, 250),
    "large": (260, 400),
    "mega": (300, 500)
}

BEHAVIOR_CAPS = {
    "small": (12, 20),
    "mid": (10, 15),
    "large": (6, 8),
    "mega": (4, 5)
}

def generate_behavior(segment, total):
    # 30% perfect customers
    if random.random() < 0.30:
        return 0, 0

    grace_cap, late_cap = BEHAVIOR_CAPS.get(segment, (10, 15))

    grace = random.randint(0, min(grace_cap, total))
    late = random.randint(0, min(late_cap, total))

    # Sanity guard
    if grace + late > total:
        late = max(0, total - grace)

    return grace, late


rows = []

for _, r in df.iterrows():
    segment = r["business_segment"]
    low, high = TOTAL_RANGES.get(segment, (25, 150))

    total = random.randint(low, high)
    payments_paid = total

    payments_in_grace, late_payments = generate_behavior(segment, total)

    updated_at = (
        r["payment_date"].date()
        if pd.notna(r["payment_date"])
        else None
    )

    rows.append((
        r["customer_id"],
        r["customer_name"],
        segment.capitalize(),
        total,
        payments_paid,
        payments_in_grace,
        late_payments,
        updated_at
    ))

# ---------- DB INSERT ----------
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    port=DB_PORT,
    autocommit=True
)

cursor = conn.cursor()

sql = """
INSERT INTO customer_payment_history(
    customer_id,
    customer_name,
    business_segment,
    total_payments,
    payments_paid,
    payments_in_grace,
    late_payments,
    updated_at
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
"""

cursor.executemany(sql, rows)

cursor.close()
conn.close()

print(f"SUCCESS: Inserted {len(rows)} historical records")
