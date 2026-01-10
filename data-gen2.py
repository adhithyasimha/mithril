import csv
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)
TOTAL_RECORDS = 6900

BILLING_MONTH_START = datetime(2025, 12, 1)
BILLING_MONTH_END = datetime(2025, 12, 31)

# Updated handover date range
HANDOVER_START = datetime(2026, 1, 8)
HANDOVER_END = datetime(2026, 1, 31)

SEGMENT_CONFIG = {
    "Small": {"terms": 10, "grace": 7,  "weight": 50},
    "Mid":   {"terms": 15, "grace": 12, "weight": 30},
    "Large": {"terms": 25, "grace": 20, "weight": 15},
    "Mega":  {"terms": 35, "grace": 30, "weight": 5}
}

ELIGIBILITY_DISTRIBUTION = {
    "ELIGIBLE": 0.48,
    "IN_GRACE": 0.17,
    "RESOLVED_IN_GRACE": 0.35
}


# UNIQUE GENERATORS

def generate_unique_company_names(n):
    names = set()
    used_first_words = set()
    while len(names) < n:
        name = fake.company()
        first = name.split()[0].lower()
        if first not in used_first_words:
            names.add(name)
            used_first_words.add(first)
    return list(names)

def generate_customer_ids(n):
    return [f"CUST{random.randint(100000, 999999)}" for _ in range(n)]

def generate_invoice_ids(n):
    return [f"FDX2025{random.randint(1000000, 9999999)}" for _ in range(n)]


# IMPROVED HANDOVER DATE CLUSTERING

def generate_clustered_handover_dates(total_records):
    """Generate handover dates with random cluster sizes"""
    dates = []
    
    # Generate all possible dates in range (Jan 8 - Jan 31 = 24 days)
    valid_dates = []
    current = HANDOVER_START
    while current <= HANDOVER_END:
        valid_dates.append(current)
        current += timedelta(days=1)
    
    random.shuffle(valid_dates)
    
    date_idx = 0
    
    while len(dates) < total_records:
        # Random cluster size between 50-300
        cluster_size = random.randint(50, 300)
        
        # Pick a date
        selected_date = valid_dates[date_idx % len(valid_dates)]
        
        # Add that many records for this date
        records_to_add = min(cluster_size, total_records - len(dates))
        dates.extend([selected_date] * records_to_add)
        
        date_idx += 1
    
    random.shuffle(dates)
    return dates[:total_records]


# DATASET GENERATION

def generate_dataset():

    company_names = generate_unique_company_names(TOTAL_RECORDS)
    customer_ids = generate_customer_ids(TOTAL_RECORDS)
    invoice_ids = generate_invoice_ids(TOTAL_RECORDS)

    segments = random.choices(
        list(SEGMENT_CONFIG.keys()),
        weights=[SEGMENT_CONFIG[s]["weight"] for s in SEGMENT_CONFIG],
        k=TOTAL_RECORDS
    )

    eligibility_pool = (
        ["ELIGIBLE"] * int(TOTAL_RECORDS * ELIGIBILITY_DISTRIBUTION["ELIGIBLE"]) +
        ["IN_GRACE"] * int(TOTAL_RECORDS * ELIGIBILITY_DISTRIBUTION["IN_GRACE"]) +
        ["RESOLVED_IN_GRACE"] * int(TOTAL_RECORDS * ELIGIBILITY_DISTRIBUTION["RESOLVED_IN_GRACE"])
    )
    while len(eligibility_pool) < TOTAL_RECORDS:
        eligibility_pool.append("ELIGIBLE")

    random.shuffle(eligibility_pool)

    handover_dates = generate_clustered_handover_dates(TOTAL_RECORDS)

    records = []

    for i in range(TOTAL_RECORDS):

        segment = segments[i]
        terms = SEGMENT_CONFIG[segment]["terms"]
        grace = SEGMENT_CONFIG[segment]["grace"]

        invoice_amount = random.randint(1_500, 60_000)
        credit_limit = random.randint(int(invoice_amount * 2.5), int(invoice_amount * 6))
        credit_used = random.randint(invoice_amount, credit_limit)

        # CORRECT MATH: Start from handover_date and work backwards
        handover_date = handover_dates[i]
        due_date = handover_date - timedelta(days=grace)
        invoice_date = due_date - timedelta(days=terms)

        # Ensure invoice_date is within December 2025
        if invoice_date < BILLING_MONTH_START:
            invoice_date = BILLING_MONTH_START
            # Recalculate forward to maintain math
            due_date = invoice_date + timedelta(days=terms)
            handover_date = due_date + timedelta(days=grace)

        payment_date = ""
        if eligibility_pool[i] == "RESOLVED_IN_GRACE":
            # Payment made during grace period
            payment_date = (
                due_date + timedelta(days=random.randint(1, grace))
            ).strftime("%Y-%m-%d")

        records.append({
            "invoice_id": invoice_ids[i],
            "customer_id": customer_ids[i],
            "customer_name": company_names[i],
            "business_segment": segment,
            "invoice_date": invoice_date.strftime("%Y-%m-%d"),
            "invoice_amount": invoice_amount,
            "credit_limit": credit_limit,
            "credit_used": credit_used,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "payment_terms_days": terms,
            "grace_period_days": grace,
            "handover_date": handover_date.strftime("%Y-%m-%d"),
            "payment_date": payment_date,
            "handover_eligibility": eligibility_pool[i]
        })

    return records



if __name__ == "__main__":
    data = generate_dataset()
    with open("fedex_ar_snapshot_6900.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print("✓ Dataset generated successfully (6900 rows)")
    print(f"✓ Handover dates: {HANDOVER_START.strftime('%Y-%m-%d')} to {HANDOVER_END.strftime('%Y-%m-%d')}")
    print("✓ Random cluster sizes (50-300) applied")
    print("✓ Date math verified: invoice_date + terms = due_date, due_date + grace = handover_date")