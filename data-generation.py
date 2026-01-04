import csv
import random
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from faker import Faker

fake = Faker()

def generate_unique_business_names(total_needed):

    
    mega_companies = [
        'Sysco Corporation',
        'McKesson Medical Supply',
        'Cardinal Health Services',
        'AmerisourceBergen Distribution',
        'US Foods Holdings',
        'Performance Food Group',
        'Genuine Parts Company',
        'LKQ Corporation',
        'WESCO International',
        'HD Supply Holdings',
        'Fastenal Company',
        'WW Grainger Inc',
        'Henry Schein Inc',
        'Patterson Companies',
        'Medline Industries',
        'Owens & Minor',
        'Ryder System Inc',
        'Americold Logistics'
    ]
    
    business_types = [
        'Industries', 'Corporation', 'Holdings', 'Group', 'Partners',
        'Supply', 'Distribution', 'Logistics', 'Manufacturing', 'Services',
        'Solutions', 'Systems', 'International', 'Enterprises', 'Company',
        'Technologies', 'Equipment', 'Materials', 'Wholesale', 'Trading',
        'Medical', 'Healthcare', 'Pharmaceuticals', 'Electronics', 'Automotive'
    ]
    
    generated_names = set()
    used_first_words = set()
    
    for name in mega_companies[:min(len(mega_companies), total_needed // 20)]:
        generated_names.add(name)
        first_word = name.split()[0].lower().strip()
        used_first_words.add(first_word)
    
    attempts = 0
    max_attempts = total_needed * 50
    
    while len(generated_names) < total_needed and attempts < max_attempts:
        attempts += 1
        
        pattern_choice = random.randint(1, 6)
        
        if pattern_choice == 1:
            name = fake.company()
        elif pattern_choice == 2:
            city = fake.city()
            biz_type = random.choice(business_types)
            name = f"{city} {biz_type}"
        elif pattern_choice == 3:
            last_name = fake.last_name()
            biz_type = random.choice(business_types)
            name = f"{last_name} {biz_type}"
        elif pattern_choice == 4:
            state = fake.state()
            biz_type = random.choice(business_types)
            name = f"{state} {biz_type}"
        elif pattern_choice == 5:
            word = fake.word().capitalize()
            biz_type = random.choice(business_types)
            name = f"{word} {biz_type}"
        else:
            unique_word = fake.company().split()[0]
            biz_type = random.choice(business_types)
            name = f"{unique_word} {biz_type}"
        
        first_word = name.split()[0].lower().strip()
        
        if name not in generated_names and first_word not in used_first_words:
            generated_names.add(name)
            used_first_words.add(first_word)
    
    counter = 1
    while len(generated_names) < total_needed:
        unique_prefix = f"Enterprise{counter}"
        biz_type = random.choice(business_types)
        name = f"{unique_prefix} {biz_type}"
        first_word = name.split()[0].lower().strip()
        
        if first_word not in used_first_words:
            generated_names.add(name)
            used_first_words.add(first_word)
        counter += 1
    
    return list(generated_names)

def generate_dataset(num_records=1200):
    
    all_business_names = generate_unique_business_names(num_records)
    random.shuffle(all_business_names)
    
    customer_ids = set()
    while len(customer_ids) < num_records:
        random_id = random.randint(100000, 999999)
        customer_ids.add(f"CUST{random_id}")
    customer_ids = list(customer_ids)
    random.shuffle(customer_ids)
    
    invoice_numbers = set()
    while len(invoice_numbers) < num_records:
        random_inv = random.randint(100000, 999999)
        invoice_numbers.add(f"FDX2025{random_inv}")
    invoice_numbers = list(invoice_numbers)
    random.shuffle(invoice_numbers)
    
    # Segment distribution
    segment_counts = {
        'Small': int(num_records * 0.50),
        'Mid': int(num_records * 0.30),
        'Large': int(num_records * 0.15),
        'Mega': int(num_records * 0.05)
    }
    
    segments = []
    for segment, count in segment_counts.items():
        segments.extend([segment] * count)
    
    while len(segments) < num_records:
        segments.append('Small')
    segments = segments[:num_records]
    random.shuffle(segments)
    
    # Payment terms by segment
    payment_terms_map = {
        'Small': 15,
        'Mid': 20,
        'Large': 30,
        'Mega': 45
    }
    
    dataset = []
    
    # Only December 2025 monthly credit cycle
    available_months = [
        datetime(2025, 12, 1)
    ]
    
    for i in range(num_records):
        segment = segments[i]
        customer_name = all_business_names[i]
        
        # Credit limits by segment
        if segment == 'Small':
            credit_limit = random.randint(5000, 50000)
            invoice_amount = random.randint(500, int(credit_limit * 0.4))
        elif segment == 'Mid':
            credit_limit = random.randint(50000, 250000)
            invoice_amount = random.randint(2000, int(credit_limit * 0.35))
        elif segment == 'Large':
            credit_limit = random.randint(250000, 750000)
            invoice_amount = random.randint(10000, int(credit_limit * 0.3))
        else:  # Mega
            credit_limit = random.randint(1000000, 3000000)
            invoice_amount = random.randint(50000, int(credit_limit * 0.25))
        
        # Credit used logic - realistic scenarios
        scenario = random.choice([1, 2, 3])
        
        if scenario == 1:
            # Scenario 1: This invoice is part of total credit used (they have other invoices/transactions)
            # credit_used must be >= invoice_amount
            other_usage = random.randint(0, int(credit_limit * 0.5))
            credit_used = invoice_amount + other_usage
            # Make sure we don't exceed credit limit
            credit_used = min(credit_used, int(credit_limit * 0.95))
            
        elif scenario == 2:
            # Scenario 2: This is their only outstanding invoice
            # credit_used == invoice_amount
            credit_used = invoice_amount
            
        else:
            # Scenario 3: They have previous balance plus this invoice
            # Previous balance (could be from paid or unpaid invoices)
            previous_balance = random.randint(int(invoice_amount * 0.5), int(credit_limit * 0.4))
            credit_used = previous_balance + invoice_amount
            # Make sure we don't exceed credit limit
            credit_used = min(credit_used, int(credit_limit * 0.95))
        
        # Final safety check - credit_used should always be >= invoice_amount
        if credit_used < invoice_amount:
            credit_used = invoice_amount
        
        # Select random month
        base_month = random.choice(available_months)
        
        # Get payment terms for this segment
        payment_terms = payment_terms_map[segment]
        
        # Generate invoice date uniformly within the month (days 1-28 to be safe)
        invoice_day = random.randint(1, 28)
        invoice_date = base_month.replace(day=invoice_day)
        
        # Due date = invoice_date + payment_terms, must be in same month
        # Calculate max possible invoice day to keep due date in same month
        last_day_of_month = (base_month + relativedelta(months=1) - timedelta(days=1)).day
        max_invoice_day = last_day_of_month - payment_terms
        
        if max_invoice_day < 1:
            # Payment term too long for this month, adjust invoice date
            max_invoice_day = 1
        
        # Regenerate invoice date if needed
        if invoice_day > max_invoice_day:
            invoice_day = random.randint(1, max(1, max_invoice_day))
            invoice_date = base_month.replace(day=invoice_day)
        
        # Calculate due date
        due_date = invoice_date + timedelta(days=payment_terms)
        
        # Ensure due date is in same month - if not, adjust
        if due_date.month != invoice_date.month or due_date.year != invoice_date.year:
            # Set due date to last day of invoice month
            due_date = (base_month + relativedelta(months=1) - timedelta(days=1))
        
        # Payment probability by segment (more unpaid for realistic DCA)
        payment_probabilities = {
            'Small': 0.55,   # 45% unpaid
            'Mid': 0.65,     # 35% unpaid
            'Large': 0.75,   # 25% unpaid
            'Mega': 0.85     # 15% unpaid
        }
        
        is_paid = random.random() < payment_probabilities[segment]
        
        if is_paid:

            # Random 1, 3, 5, 7 days before due date or on due date
            days_before_due = random.choice([0, 1, 3, 5, 7])
            payment_date = due_date - timedelta(days=days_before_due)
            
            # Make sure payment date is not before invoice date
            if payment_date < invoice_date:
                # Pay somewhere between invoice and due date
                days_diff = (due_date - invoice_date).days
                if days_diff > 0:
                    payment_date = invoice_date + timedelta(days=random.randint(1, days_diff))
                else:
                    payment_date = invoice_date
            
            payment_status = 'Paid'
            amount_paid = invoice_amount
        else:
            payment_date = None
            payment_status = 'Unpaid'
            amount_paid = None
        
        # Create record
        record = {
            'customer_id': customer_ids[i],
            'customer_name': customer_name,
            'business_segment': segment,
            'invoice_number': invoice_numbers[i],
            'invoice_date': invoice_date.strftime('%Y-%m-%d'),
            'invoice_amount': invoice_amount,
            'credit_limit': credit_limit,
            'credit_used': credit_used,
            'due_date': due_date.strftime('%Y-%m-%d'),
            'payment_date': payment_date.strftime('%Y-%m-%d') if payment_date else '',
            'amount_paid': amount_paid if amount_paid else '',
            'payment_status': payment_status
        }
        
        dataset.append(record)
    
    return dataset

def save_to_csv(dataset, filename='fedex_dca_dataset.csv'):
    
    home_dir = os.path.expanduser('~')
    filepath = os.path.join(home_dir, filename)
    
    fieldnames = [
        'customer_id', 'customer_name', 'business_segment', 'invoice_number',
        'invoice_date', 'invoice_amount', 'credit_limit', 'credit_used',
        'due_date', 'payment_date', 'amount_paid', 'payment_status'
    ]
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset)
    
    print(f"\n✓ Dataset saved to '{filepath}'")
    
    # Print statistics
    total = len(dataset)
    paid = sum(1 for row in dataset if row['payment_status'] == 'Paid')
    unpaid = total - paid
    
    segments = {}
    for row in dataset:
        seg = row['business_segment']
        segments[seg] = segments.get(seg, 0) + 1
    
    print(f"\n=== Dataset Statistics ===")
    print(f"Total Records: {total}")
    print(f"Paid: {paid} ({paid/total*100:.1f}%)")
    print(f"Unpaid: {unpaid} ({unpaid/total*100:.1f}%)")
    print(f"\nBy Segment:")
    for seg, count in sorted(segments.items()):
        print(f"  {seg}: {count} ({count/total*100:.1f}%)")
    
    # Check for duplicates
    names = [row['customer_name'] for row in dataset]
    duplicates = len(names) - len(set(names))
    print(f"\nDuplicate business names: {duplicates}")
    
    # Check for duplicate first words - STRICT
    first_words = [name.split()[0].lower().strip() for name in names]
    duplicate_first_words = len(first_words) - len(set(first_words))
    print(f"Duplicate first words: {duplicate_first_words}")
    
    # Validate date logic and credit logic
    print(f"\n=== Date Validation ===")
    date_errors = 0
    credit_errors = 0
    for row in dataset:
        inv_date = datetime.strptime(row['invoice_date'], '%Y-%m-%d')
        due_date = datetime.strptime(row['due_date'], '%Y-%m-%d')
        
        # Check credit logic
        if row['credit_used'] < row['invoice_amount']:
            credit_errors += 1
        
        if row['payment_date']:
            pay_date = datetime.strptime(row['payment_date'], '%Y-%m-%d')
            if pay_date > due_date or pay_date < inv_date:
                date_errors += 1
    
    print(f"Date logic errors (payment before invoice or after due): {date_errors}")
    print(f"Credit logic errors (credit_used < invoice_amount): {credit_errors}")

if __name__ == "__main__":
    num_records = 1200
    dataset = generate_dataset(num_records)


    save_to_csv(dataset)
    
