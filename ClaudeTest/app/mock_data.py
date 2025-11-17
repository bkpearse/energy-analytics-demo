"""
Mock data for demonstration purposes.
Simulates an energy B2B sales database without requiring PostgreSQL.
"""
import pandas as pd
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
random.seed(42)


def generate_mock_data():
    """Generate all mock data tables."""

    # Sales Representatives
    sales_reps = pd.DataFrame({
        'sales_rep_id': ['SR001', 'SR002', 'SR003', 'SR004', 'SR005', 'SR006', 'SR007', 'SR008'],
        'first_name': ['John', 'Sarah', 'Michael', 'Emma', 'David', 'Lisa', 'James', 'Rachel'],
        'last_name': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'],
        'email': ['john.smith@company.com', 'sarah.johnson@company.com', 'michael.williams@company.com',
                 'emma.brown@company.com', 'david.jones@company.com', 'lisa.garcia@company.com',
                 'james.miller@company.com', 'rachel.davis@company.com'],
        'team': ['North', 'North', 'South', 'South', 'East', 'East', 'West', 'West'],
        'hire_date': pd.to_datetime(['2020-01-15', '2019-06-20', '2021-03-10', '2020-08-05',
                                     '2019-11-12', '2021-07-01', '2020-02-28', '2021-09-15']),
        'status': ['Active'] * 8
    })

    # Customers
    customers = pd.DataFrame({
        'customer_id': [f'CUST{i:03d}' for i in range(1, 31)],
        'company_name': [
            'TechCorp Industries', 'Green Energy Solutions', 'Manufacturing Plus Ltd',
            'Retail Dynamics Inc', 'Healthcare Systems Co', 'Logistics Masters',
            'DataCenter Operations', 'Food Processing Ltd', 'Automotive Group',
            'Chemical Industries', 'Textile Manufacturing', 'Electronics Corp',
            'Pharmaceutical Labs', 'Construction Materials', 'Paper Products Inc',
            'Steel Works Ltd', 'Plastics Manufacturing', 'Beverage Company',
            'Furniture Makers', 'Glass Industries', 'Cement Corporation',
            'Oil & Gas Services', 'Mining Operations', 'Aerospace Parts',
            'Marine Equipment', 'Agricultural Processing', 'Printing Services',
            'Packaging Solutions', 'Waste Management Co', 'Recycling Industries'
        ],
        'industry': [
            'Technology', 'Energy', 'Manufacturing', 'Retail', 'Healthcare',
            'Logistics', 'Technology', 'Food & Beverage', 'Automotive', 'Chemicals',
            'Textiles', 'Electronics', 'Pharmaceuticals', 'Construction', 'Paper',
            'Steel', 'Plastics', 'Food & Beverage', 'Furniture', 'Glass',
            'Construction', 'Oil & Gas', 'Mining', 'Aerospace', 'Marine',
            'Agriculture', 'Printing', 'Packaging', 'Waste Management', 'Recycling'
        ],
        'account_status': ['Active'] * 25 + ['Prospect'] * 5,
        'created_date': pd.to_datetime([datetime.now() - timedelta(days=random.randint(100, 800)) for _ in range(30)]),
        'annual_consumption_kwh': [random.randint(100000, 5000000) for _ in range(30)],
        'account_manager_id': [random.choice(sales_reps['sales_rep_id'].tolist()) for _ in range(30)]
    })

    # Products
    products = pd.DataFrame({
        'product_id': ['PROD001', 'PROD002', 'PROD003', 'PROD004', 'PROD005', 'PROD006'],
        'product_name': [
            'Standard Fixed Rate Plan',
            'Variable Rate Plan',
            'Green Energy Premium',
            'Industrial Bulk Supply',
            'Peak Demand Management',
            'Renewable Energy Credits'
        ],
        'product_category': ['Fixed Rate', 'Variable Rate', 'Renewable', 'Bulk Supply', 'Demand Management', 'Credits'],
        'unit_type': ['kWh', 'kWh', 'kWh', 'kWh', 'kW', 'REC'],
        'base_price': [0.085, 0.075, 0.095, 0.070, 0.120, 0.005],
        'is_active': [True] * 6
    })

    # Deals
    deal_stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
    num_deals = 80

    deals_data = []
    for i in range(1, num_deals + 1):
        stage = random.choice(deal_stages)
        created = datetime.now() - timedelta(days=random.randint(1, 365))

        if stage == 'Closed Won':
            close_date = created + timedelta(days=random.randint(30, 120))
            probability = 100
        elif stage == 'Closed Lost':
            close_date = created + timedelta(days=random.randint(30, 120))
            probability = 0
        else:
            close_date = None
            probability = {'Prospecting': 10, 'Qualification': 25, 'Proposal': 50, 'Negotiation': 75}[stage]

        deal_value = random.randint(20000, 500000)

        deals_data.append({
            'deal_id': f'DEAL{i:03d}',
            'deal_name': f'{random.choice(customers["company_name"].tolist())} - Energy Contract',
            'customer_id': random.choice(customers['customer_id'].tolist()),
            'sales_rep_id': random.choice(sales_reps['sales_rep_id'].tolist()),
            'deal_stage': stage,
            'deal_value': deal_value,
            'probability': probability,
            'expected_close_date': created + timedelta(days=random.randint(60, 180)) if stage not in ['Closed Won', 'Closed Lost'] else None,
            'actual_close_date': close_date,
            'created_date': created,
            'contract_start_date': close_date if stage == 'Closed Won' else None,
            'contract_end_date': close_date + timedelta(days=365) if stage == 'Closed Won' else None,
            'contract_term_months': 12 if stage == 'Closed Won' else None
        })

    deals = pd.DataFrame(deals_data)

    # Deal Line Items
    line_items_data = []
    line_item_id = 1
    for _, deal in deals.iterrows():
        num_items = random.randint(1, 3)
        for _ in range(num_items):
            product = products.sample(1).iloc[0]
            quantity = random.randint(50000, 2000000)
            unit_price = product['base_price'] * random.uniform(0.9, 1.1)
            discount = random.choice([0, 5, 10, 15])
            total = quantity * unit_price * (1 - discount/100)

            line_items_data.append({
                'line_item_id': f'LINE{line_item_id:04d}',
                'deal_id': deal['deal_id'],
                'product_id': product['product_id'],
                'quantity': quantity,
                'unit_price': round(unit_price, 4),
                'discount_percent': discount,
                'total_price': round(total, 2),
                'estimated_kwh': quantity if product['unit_type'] == 'kWh' else 0
            })
            line_item_id += 1

    deal_line_items = pd.DataFrame(line_items_data)

    # Commission Tiers
    commission_tiers = pd.DataFrame({
        'tier_id': ['TIER1', 'TIER2', 'TIER3', 'TIER4'],
        'tier_name': ['Bronze', 'Silver', 'Gold', 'Platinum'],
        'min_value': [0, 100000, 250000, 500000],
        'max_value': [99999, 249999, 499999, 999999999],
        'commission_rate': [0.02, 0.03, 0.04, 0.05],
        'effective_from': pd.to_datetime('2023-01-01'),
        'effective_to': pd.to_datetime('2025-12-31')
    })

    # Commissions
    commissions_data = []
    commission_id = 1
    for _, deal in deals[deals['deal_stage'] == 'Closed Won'].iterrows():
        # Determine tier
        value = deal['deal_value']
        if value < 100000:
            rate = 0.02
        elif value < 250000:
            rate = 0.03
        elif value < 500000:
            rate = 0.04
        else:
            rate = 0.05

        commission_amount = value * rate
        payment_date = deal['actual_close_date'] + timedelta(days=random.randint(30, 60))

        commissions_data.append({
            'commission_id': f'COMM{commission_id:04d}',
            'sales_rep_id': deal['sales_rep_id'],
            'deal_id': deal['deal_id'],
            'commission_amount': round(commission_amount, 2),
            'commission_rate': rate,
            'payment_date': payment_date,
            'payment_status': random.choice(['Paid', 'Pending']) if payment_date <= datetime.now() else 'Pending',
            'calculation_date': deal['actual_close_date'],
            'notes': None
        })
        commission_id += 1

    commissions = pd.DataFrame(commissions_data)

    # Activities
    activities_data = []
    activity_types = ['Call', 'Meeting', 'Email', 'Demo', 'Follow-up']
    outcomes = ['Positive', 'Neutral', 'Negative', 'Scheduled Next Meeting', 'Sent Proposal']

    for i in range(1, 201):
        deal = deals.sample(1).iloc[0]
        activity_date = deal['created_date'] + timedelta(days=random.randint(0, 90))

        activities_data.append({
            'activity_id': f'ACT{i:04d}',
            'activity_type': random.choice(activity_types),
            'subject': f'{random.choice(activity_types)} regarding energy contract',
            'customer_id': deal['customer_id'],
            'deal_id': deal['deal_id'],
            'sales_rep_id': deal['sales_rep_id'],
            'activity_date': activity_date,
            'duration_minutes': random.choice([15, 30, 45, 60]) if random.random() > 0.3 else None,
            'outcome': random.choice(outcomes),
            'notes': None
        })

    activities = pd.DataFrame(activities_data)

    return {
        'customers': customers,
        'sales_reps': sales_reps,
        'deals': deals,
        'products': products,
        'deal_line_items': deal_line_items,
        'commission_tiers': commission_tiers,
        'commissions': commissions,
        'activities': activities
    }


def get_sales_pipeline_view(deals, customers, sales_reps):
    """Generate sales_pipeline view."""
    pipeline = deals.merge(customers[['customer_id', 'company_name']], on='customer_id', how='left')
    pipeline = pipeline.merge(
        sales_reps[['sales_rep_id', 'first_name', 'last_name']],
        on='sales_rep_id',
        how='left'
    )
    pipeline['sales_rep_name'] = pipeline['first_name'] + ' ' + pipeline['last_name']

    def get_status(row):
        if row['actual_close_date'] is not None and not pd.isna(row['actual_close_date']):
            return 'Closed'
        elif row['expected_close_date'] is not None and not pd.isna(row['expected_close_date']):
            if row['expected_close_date'] < datetime.now():
                return 'Overdue'
        return 'Open'

    pipeline['pipeline_status'] = pipeline.apply(get_status, axis=1)

    return pipeline[[
        'deal_id', 'deal_name', 'company_name', 'sales_rep_name',
        'deal_stage', 'deal_value', 'probability', 'expected_close_date',
        'actual_close_date', 'pipeline_status'
    ]]


def get_monthly_sales_performance_view(deals, sales_reps, commissions):
    """Generate monthly_sales_performance view."""
    closed_deals = deals[deals['deal_stage'] == 'Closed Won'].copy()

    if closed_deals.empty:
        return pd.DataFrame(columns=[
            'month', 'sales_rep_id', 'sales_rep_name', 'team',
            'deals_closed', 'total_revenue', 'avg_deal_size', 'total_commission'
        ])

    closed_deals['month'] = pd.to_datetime(closed_deals['actual_close_date']).dt.to_period('M').dt.to_timestamp()

    # Merge with sales reps
    performance = closed_deals.merge(
        sales_reps[['sales_rep_id', 'first_name', 'last_name', 'team']],
        on='sales_rep_id',
        how='left'
    )
    performance['sales_rep_name'] = performance['first_name'] + ' ' + performance['last_name']

    # Aggregate by month and rep
    monthly = performance.groupby(['month', 'sales_rep_id', 'sales_rep_name', 'team']).agg({
        'deal_id': 'count',
        'deal_value': ['sum', 'mean']
    }).reset_index()

    monthly.columns = ['month', 'sales_rep_id', 'sales_rep_name', 'team', 'deals_closed', 'total_revenue', 'avg_deal_size']

    # Add commission data
    commission_monthly = commissions.copy()
    commission_monthly['month'] = pd.to_datetime(commission_monthly['payment_date']).dt.to_period('M').dt.to_timestamp()
    commission_totals = commission_monthly.groupby(['month', 'sales_rep_id'])['commission_amount'].sum().reset_index()
    commission_totals.columns = ['month', 'sales_rep_id', 'total_commission']

    monthly = monthly.merge(commission_totals, on=['month', 'sales_rep_id'], how='left')
    monthly['total_commission'] = monthly['total_commission'].fillna(0)

    return monthly


# Initialize data on module import
MOCK_DATA = generate_mock_data()
