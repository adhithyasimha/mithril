import boto3
import pymysql
import csv
import io
import os
from datetime import datetime

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]   
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_PORT = 3306

TABLE_NAME = "case_table"
PRIMARY_KEY = "case_id"

s3 = boto3.client("s3")

def parse_date(val):
    return val if val else None

def parse_datetime(val):
    return datetime.strptime(val, "%Y-%m-%d %H:%M:%S") if val else None

def lambda_handler(event, context):

    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    print(f"Processing s3://{bucket}/{key}")

    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj["Body"].read().decode("utf-8")

    reader = csv.DictReader(io.StringIO(data))
    rows = list(reader)

    if not rows:
        print("Empty file")
        return

    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        autocommit=False
    )
    cur = conn.cursor()

    # 1. Check table existence
    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema=%s
          AND table_name=%s
    """, (DB_NAME, TABLE_NAME))

    if cur.fetchone()[0] == 0:
        print("Creating table case_table")

        cur.execute("""
            CREATE TABLE case_table (
              case_id VARCHAR(64) PRIMARY KEY,
              invoice_id VARCHAR(32),
              customer_id VARCHAR(32),
              customer_name VARCHAR(255),
              business_segment VARCHAR(16),
              invoice_amount INT,
              due_date DATE,
              handover_date DATE,
              case_status VARCHAR(16),
              case_created_at DATETIME
            );
        """)
        conn.commit()

    # 2. Incremental UPSERT
    insert_sql = """
        INSERT INTO case_table (
          case_id, invoice_id, customer_id, customer_name,
          business_segment, invoice_amount, due_date,
          handover_date, case_status, case_created_at
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          invoice_id=VALUES(invoice_id),
          customer_id=VALUES(customer_id),
          customer_name=VALUES(customer_name),
          business_segment=VALUES(business_segment),
          invoice_amount=VALUES(invoice_amount),
          due_date=VALUES(due_date),
          handover_date=VALUES(handover_date),
          case_status=VALUES(case_status),
          case_created_at=VALUES(case_created_at);
    """

    for r in rows:
        cur.execute(insert_sql, (
            r["case_id"],
            r["invoice_id"],
            r["customer_id"],
            r["customer_name"],
            r["business_segment"],
            int(r["invoice_amount"]),
            parse_date(r["due_date"]),
            parse_date(r["handover_date"]),
            r["case_status"],
            parse_datetime(r["case_created_at"])
        ))

    conn.commit()
    cur.close()
    conn.close()

    print(f"Upserted {len(rows)} rows into case_table")
