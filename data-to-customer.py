import pymysql
import csv
import random

# ---------- DB ----------
DB_HOST = "mithril-case-database.ctogioe46r4p.us-west-2.rds.amazonaws.com"
DB_USER = "admin"
DB_PASS = "Qwerty123$"
DB_NAME = "mithril-case-database"
DB_PORT = 3306

# ---------- CSV PATH ----------
CSV_FILE = "fedex_ar_snapshot_6900.csv" 

INSERT_QUERY = """
INSERT INTO customer (
    customer_id,
    customer_name,
    business_segment,
    credit_limit,
    tin_number,
    phone_number,
    email
)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

def generate_phone():
    return "9" + "".join(str(random.randint(0, 9)) for _ in range(9))

def generate_tin(existing):
    while True:
        tin = "".join(str(random.randint(0, 9)) for _ in range(12))
        if tin not in existing:
            existing.add(tin)
            return tin

def read_csv(filepath):
    """Read CSV and extract unique customer records"""
    customers = []
    seen_ids = set()
    duplicates = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cust_id = row['customer_id']
                
                # Skip duplicate customer_ids
                if cust_id in seen_ids:
                    duplicates += 1
                    continue
                
                seen_ids.add(cust_id)
                customers.append((
                    cust_id,
                    row['customer_name'],
                    row['business_segment'],
                    row['credit_limit']
                ))
        
        if duplicates > 0:
            print(f"Skipped {duplicates} duplicate customer_id(s) from CSV")
        
        return customers
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return []
    except KeyError as e:
        print(f"Error: Missing required column {e} in CSV")
        return []

def get_existing_customer_ids(cursor):
    """Fetch all existing customer IDs from database"""
    cursor.execute("SELECT customer_id FROM customer")
    return {row[0] for row in cursor.fetchall()}

def main():
    # Read customers from CSV
    customers = read_csv(CSV_FILE)
    
    if not customers:
        print("No customers to insert")
        return
    
    print(f"Loaded {len(customers)} unique customers from CSV")
    
    # Connect to database
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT
    )

    cursor = conn.cursor()
    
    # Get existing customer IDs from database
    print("Checking for existing customer IDs in database...")
    existing_ids = get_existing_customer_ids(cursor)
    print(f"Found {len(existing_ids)} existing customers in database")
    
    used_tins = set()
    records = []
    skipped = 0

    # Generate additional fields for each customer
    for idx, (cust_id, cust_name, segment, credit_limit) in enumerate(customers, start=1):
        # Skip if customer_id already exists in database
        if cust_id in existing_ids:
            skipped += 1
            continue
        
        email = f"psadhithya+{idx}@gmail.com"
        phone = generate_phone()
        tin = generate_tin(used_tins)

        records.append((
            cust_id,
            cust_name,
            segment,
            credit_limit,
            tin,
            phone,
            email
        ))

    if skipped > 0:
        print(f"Skipped {skipped} customers that already exist in database")
    
    if not records:
        print("No new customers to insert")
        cursor.close()
        conn.close()
        return

    # Insert into database
    print(f"Inserting {len(records)} new customers...")
    cursor.executemany(INSERT_QUERY, records)
    conn.commit()

    cursor.close()
    conn.close()

    print(f"Successfully inserted {len(records)} customers into database")

if __name__ == "__main__":
    main()