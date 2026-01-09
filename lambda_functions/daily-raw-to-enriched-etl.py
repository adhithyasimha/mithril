import boto3
import csv
from io import StringIO
from datetime import datetime, timedelta

s3 = boto3.client("s3")

SOURCE_BUCKET = "mithril-ar-raw-base"
SOURCE_KEY = "dataset-vol-6900.csv"

DEST_BUCKET = "mithril-enriched-bucket"

DATE_FMT = "%Y-%m-%d"


def lambda_handler(event, context):

    # (handover date)

    today = datetime.utcnow().date()
    handover_day = today - timedelta(days=1)

    handover_str = handover_day.strftime(DATE_FMT)          
    day_str = handover_day.strftime("%d")                   
    mon_year_str = handover_day.strftime("%b-%y").lower()   


    # Read source CSV from S3

    obj = s3.get_object(
        Bucket=SOURCE_BUCKET,
        Key=SOURCE_KEY
    )

    csv_data = obj["Body"].read().decode("utf-8")
    reader = csv.DictReader(StringIO(csv_data))

    filtered_rows = []


    # CORE BUSINESS FILTER (FINAL)
    
    for row in reader:
        if (
            row.get("handover_date", "").strip() == handover_str
            and row.get("handover_eligibility", "").strip() == "ELIGIBLE"
        ):
            filtered_rows.append(row)

    if not filtered_rows:
        print(f"No ELIGIBLE handovers for {handover_str}")
        return {
            "status": "NO_DATA",
            "handover_date": handover_str
        }


    # month folder (YYYY-MM)

    due_date = datetime.strptime(
        filtered_rows[0]["due_date"], DATE_FMT
    ).date()

    month_folder = due_date.strftime("%Y-%m")

    # Write daily snapshot to S3

    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=filtered_rows[0].keys()
    )
    writer.writeheader()
    writer.writerows(filtered_rows)

    s3_key = (
        f"{month_folder}/"
        f"handover-{day_str}-{mon_year_str}.csv"
    )

    s3.put_object(
        Bucket=DEST_BUCKET,
        Key=s3_key,
        Body=buffer.getvalue(),
        ContentType="text/csv"
    )

    print(
        f"Wrote {len(filtered_rows)} ELIGIBLE records → "
        f"s3://{DEST_BUCKET}/{s3_key}"
    )

    return {
        "status": "SUCCESS",
        "handover_date": handover_str,
        "records_written": len(filtered_rows),
        "s3_key": s3_key
    }
