"""
Create realistic validation dataset with dummy data
Simulates real-world annual report excerpts about GHG emissions
"""

import pandas as pd
import random

# Set seed for reproducibility
random.seed(42)

# Real-world company names and exchanges
companies = {
    'NYSE': [
        'General Electric', 'Chevron Corporation', 'ExxonMobil', 'Johnson & Johnson',
        'Coca-Cola', 'Walmart', 'Amazon', 'Microsoft', 'Apple', 'Tesla',
        'JPMorgan Chase', 'Bank of America', 'Goldman Sachs', 'Morgan Stanley',
        'Procter & Gamble', 'Nike', 'McDonald\'s', 'Starbucks', 'IBM', 'Intel'
    ],
    'NASDAQ': [
        'Google', 'Meta', 'Netflix', 'Adobe', 'Nvidia', 'AMD', 'Qualcomm',
        'Broadcom', 'Salesforce', 'Zoom', 'Slack', 'Shopify', 'Airbnb',
        'Tesla', 'PayPal', 'Square', 'Datadog', 'Okta', 'Twilio', 'Stripe'
    ],
    'LSE': [
        'HSBC Holdings', 'Unilever', 'Shell', 'BP', 'Barclays', 'Lloyds',
        'Diageo', 'Reckitt Benckiser', 'AstraZeneca', 'GSK', 'Rolls-Royce',
        'Glencore', 'Rio Tinto', 'Antofagasta', 'Polymetal', 'Evraz'
    ],
    'TSX': [
        'Royal Bank of Canada', 'Toronto-Dominion Bank', 'Bank of Nova Scotia',
        'Enbridge', 'TC Energy', 'Canadian Natural', 'Suncor Energy',
        'Barrick Gold', 'Agnico Eagle Mines', 'Nutrien', 'Brookfield Asset'
    ],
    'ASX': [
        'Commonwealth Bank', 'Westpac', 'ANZ', 'NAB', 'BHP', 'Rio Tinto',
        'Fortescue Metals', 'Woodside Petroleum', 'Santos', 'Telstra',
        'Wesfarmers', 'Coles Group', 'Macquarie Group', 'AMP', 'Ramsay Health'
    ]
}

# Real-world Scope 3 reporting excerpts (Label 1)
scope3_reporting = [
    "Our comprehensive GHG inventory covers Scopes 1, 2, and 3. In 2023, Scope 3 emissions totaled 45.2 million metric tons CO2e, representing 94% of our total carbon footprint. These emissions primarily stem from purchased goods and services, business travel, and employee commuting.",
    "We report emissions across all three scopes in accordance with the GHG Protocol. Scope 3 emissions were measured at 12.8 million tCO2e, with the largest contributors being upstream transportation and distribution of our products.",
    "Our Scope 1, 2, and 3 emissions inventory shows total Scope 3 emissions of 156 million metric tons CO2e. This includes categories 1-15 of the GHG Protocol, with particular focus on use of sold products and capital goods.",
    "We disclose all three scopes of greenhouse gas emissions. Scope 3 emissions totaled 8.4 million metric tons CO2e in 2022, primarily from manufacturing and logistics activities in our supply chain.",
    "Our carbon footprint includes Scope 1, 2, and 3 emissions. Scope 3 emissions were calculated at 2.1 million tCO2e, representing 87% of our total GHG footprint across all operations.",
    "We measure and report Scope 1, 2, and 3 greenhouse gas emissions annually. In 2023, our Scope 3 emissions totaled 34.5 million metric tons CO2e, with emissions data verified by third-party assurance.",
    "All three scopes of emissions are included in our GHG reporting. Scope 3 emissions of 19.7 million tCO2e were calculated using spend-based methodology for purchased goods and services.",
    "We report comprehensive Scope 1, 2, and 3 emissions data. Our Scope 3 emissions inventory includes 15 categories, totaling 78.3 million metric tons CO2e for the reporting year.",
    "Our GHG emissions table covers Scope 1, 2 and categories of Scope 3 relevant to our business. Total measured Scope 3 emissions: 764,936 tonnes CO2e, including purchased goods, transportation, and use of sold products.",
    "We calculate and disclose Scope 1, 2, and 3 emissions. Scope 3 financed emissions from our lending and investment portfolios totaled 33.1 million tCO2e, representing our climate impact in the financial sector.",
]

# Real-world non-Scope 3 reporting excerpts (Label 0)
no_scope3_reporting = [
    "Our environmental strategy focuses on reducing Scope 1 and Scope 2 emissions. In 2023, we achieved a 15% reduction in direct emissions from our facilities and operations.",
    "We report Scope 1 and Scope 2 emissions from our operations. Our Scope 1 emissions totaled 2,500 metric tons CO2e, while Scope 2 emissions were 8,900 metric tons CO2e.",
    "Our GHG emissions reporting covers Scope 1 and Scope 2 only. We are currently developing our Scope 3 emissions measurement methodology for future disclosure.",
    "We measure and report emissions from our direct operations (Scope 1) and purchased energy (Scope 2). Total emissions in 2023: 11,400 metric tons CO2e.",
    "Our carbon footprint includes emissions from company-owned vehicles and facilities (Scope 1) and purchased electricity (Scope 2). We plan to expand our reporting to include Scope 3 emissions by 2025.",
    "Scope 1 and 2 emissions are the focus of our current climate strategy. We are working to understand and audit our Scope 1 and Scope 2 carbon footprint of our operations.",
    "Our emissions inventory covers direct emissions (Scope 1) and indirect emissions from energy (Scope 2). Total measured emissions: 5,200 tCO2e in 2023.",
    "We report greenhouse gas emissions from our facilities and energy consumption. Scope 1 emissions: 1,800 tCO2e. Scope 2 emissions: 6,500 tCO2e.",
    "Our climate reporting includes Scope 1 and Scope 2 emissions. We are currently in the process of calculating our Scope 3 emissions to determine future targets.",
    "We disclose emissions from our direct operations and purchased energy. Our Scope 1 and 2 emissions totaled 9,700 metric tons CO2e in the reporting period.",
    "Our GHG protocol reporting covers Scopes 1 and 2. We have not yet begun reporting Scope 3 emissions as we develop our measurement methodology.",
    "Emissions from company operations (Scope 1) and purchased electricity (Scope 2) are reported annually. Total: 7,300 tCO2e. Scope 3 reporting planned for next year.",
    "We measure direct emissions from our facilities and indirect emissions from purchased energy. Our combined Scope 1 and 2 emissions: 4,100 metric tons CO2e.",
    "Our environmental reporting focuses on Scope 1 and Scope 2 emissions. We are developing our Scope 3 emissions assessment and plan to report next year.",
    "Scope 1 and 2 emissions are currently reported. We are working toward comprehensive Scope 3 emissions reporting in the coming years.",
]

# Generate validation dataset
validation_data = []

# Generate 60 validation samples
for i in range(60):
    exchange = random.choice(list(companies.keys()))
    company = random.choice(companies[exchange])
    year = random.choice([2021, 2022, 2023, 2024])
    
    # 40% chance of Scope 3 reporting (Label 1), 60% no Scope 3 (Label 0)
    if random.random() < 0.4:
        # Label 1: Scope 3 reporting
        excerpt = random.choice(scope3_reporting)
        label = 1
    else:
        # Label 0: No Scope 3 reporting
        excerpt = random.choice(no_scope3_reporting)
        label = 0
    
    validation_data.append({
        'company_name': company,
        'exchange': exchange,
        'year': year,
        'text_excerpt': excerpt,
        'label': label
    })

# Create DataFrame
df = pd.DataFrame(validation_data)

# Save to CSV
output_file = 'validation.csv'
df.to_csv(output_file, index=False)

print("="*70)
print("VALIDATION DATASET CREATED")
print("="*70)
print(f"\n✓ File: {output_file}")
print(f"✓ Total rows: {len(df)}")
print(f"✓ Label 0 (No Scope 3): {(df['label']==0).sum()} ({(df['label']==0).sum()/len(df)*100:.1f}%)")
print(f"✓ Label 1 (Scope 3): {(df['label']==1).sum()} ({(df['label']==1).sum()/len(df)*100:.1f}%)")
print(f"✓ Unique companies: {df['company_name'].nunique()}")
print(f"✓ Exchanges: {sorted(df['exchange'].unique().tolist())}")
print(f"✓ Years: {sorted(df['year'].unique().tolist())}")
print(f"✓ Text excerpt length: {df['text_excerpt'].str.len().min()}-{df['text_excerpt'].str.len().max()} chars")

print("\n" + "="*70)
print("SAMPLE ROWS")
print("="*70)
for idx, row in df.head(5).iterrows():
    print(f"\nRow {idx+1}:")
    print(f"  Company: {row['company_name']}")
    print(f"  Exchange: {row['exchange']}")
    print(f"  Year: {row['year']}")
    print(f"  Label: {row['label']}")
    print(f"  Excerpt: {row['text_excerpt'][:100]}...")

print("\n" + "="*70)
print("NEXT STEP: Run evaluation")
print("="*70)
print("$ python training_script.py --validation validation.csv")
print("="*70)
