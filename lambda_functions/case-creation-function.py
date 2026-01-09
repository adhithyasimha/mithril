import boto3
import csv
import hashlib
from io import StringIO
from datetime import datetime
import urllib.parse

s3 = boto3.client("s3")
DEST_BUCKET = "mithril-case-bucket"
DATE_FMT = "%Y-%m-%d"

# UNIQUE CASE ID HELPERS

def generate_unique_8_digit(invoice_id, customer_id, handover_date):
    raw = f"{invoice_id}|{customer_id}|{handover_date}"
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return str(int(digest[:10], 16) % 100_000_000).zfill(8)


def generate_case_id(segment, invoice_id, customer_id, handover_date):
    return (
        f"CASE-{segment.upper()}-"
        f"{handover_date.strftime('%Y%m%d')}-"
        f"{generate_unique_8_digit(invoice_id, customer_id, handover_date)}"
    )



def lambda_handler(event, context):


    record = event["Records"][0]

    source_bucket = record["s3"]["bucket"]["name"]
    source_key = urllib.parse.unquote_plus(
        record["s3"]["object"]["key"]
    )

    print(f"Triggered by: s3://{source_bucket}/{source_key}")

    # Safety: ignore non-handover files
   
    if not source_key.endswith(".csv") or "handover-" not in source_key:
        print("Ignoring non-handover file")
        return {"status": "IGNORED"}
    obj = s3.get_object(
        Bucket=source_bucket,
        Key=source_key
    )

    csv_data = obj["Body"].read().decode("utf-8")
    reader = csv.DictReader(StringIO(csv_data))

    cases = []
    now_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for row in reader:
        handover_date = datetime.strptime(
            row["handover_date"], DATE_FMT
        ).date()

        cases.append({
            "case_id": generate_case_id(
                row["business_segment"],
                row["invoice_id"],
                row["customer_id"],
                handover_date
            ),
            "invoice_id": row["invoice_id"],
            "customer_id": row["customer_id"],
            "customer_name": row["customer_name"],
            "business_segment": row["business_segment"],
            "invoice_amount": row["invoice_amount"],
            "due_date": row["due_date"],
            "handover_date": row["handover_date"],
            "case_status": "OPEN",
            "case_created_at": now_ts
        })

    if not cases:
        print("No cases created (empty file)")
        return {"status": "NO_CASES"}

    
    # Build destination key
    # Preserve YYYY-MM folder
    month_folder = source_key.split("/")[0]


    filename = source_key.split("/")[-1].replace(
        "handover", "cases"
    )

    dest_key = f"{month_folder}/{filename}"

    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=cases[0].keys()
    )
    writer.writeheader()
    writer.writerows(cases)

    s3.put_object(
        Bucket=DEST_BUCKET,
        Key=dest_key,
        Body=buffer.getvalue(),
        ContentType="text/csv"
    )

    print(
        f"Created {len(cases)} cases → "
        f"s3://{DEST_BUCKET}/{dest_key}"
    )

    return {
        "status": "SUCCESS",
        "source_file": source_key,
        "cases_created": len(cases),
        "dest_key": dest_key
    }
