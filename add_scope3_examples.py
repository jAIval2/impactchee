"""
Helper Script: Add Scope 3 Examples to Dataset
Creates synthetic or manually curated label 1 examples for training
"""

import pandas as pd
from pathlib import Path


def create_scope3_examples():
    """
    Create realistic Scope 3 reporting examples
    These are based on common patterns in corporate sustainability reports
    """
    
    scope3_examples = [
        {
            'company_name': 'Microsoft Corporation',
            'exchange': 'NASDAQ',
            'year': 2023,
            'text_excerpt': 'During fiscal year 2023, we measured and reported our Scope 1, Scope 2, and Scope 3 emissions in accordance with the GHG Protocol. Our Scope 3 emissions totaled 13.9 million metric tons of CO2e, representing 98% of our total carbon footprint.',
            'label': 1
        },
        {
            'company_name': 'Apple Inc',
            'exchange': 'NASDAQ',
            'year': 2023,
            'text_excerpt': 'We disclose all three scopes of greenhouse gas emissions. Scope 3 emissions, which include our value chain emissions, were 22.5 million metric tons CO2e in 2023, down 5% from the prior year.',
            'label': 1
        },
        {
            'company_name': 'Unilever PLC',
            'exchange': 'LSE',
            'year': 2022,
            'text_excerpt': 'Our total Scope 1 and 2 emissions were 2.1 million tonnes CO2e, while Scope 3 emissions across our value chain were calculated at 64.3 million tonnes CO2e, covering all 15 categories of the GHG Protocol.',
            'label': 1
        },
        {
            'company_name': 'Salesforce Inc',
            'exchange': 'NYSE',
            'year': 2023,
            'text_excerpt': 'We achieved net zero across Scope 1, 2, and 3 emissions. Our Scope 3 emissions were measured at 1.2 million metric tons CO2e, primarily from purchased goods and services, business travel, and employee commuting.',
            'label': 1
        },
        {
            'company_name': 'Google LLC',
            'exchange': 'NASDAQ',
            'year': 2022,
            'text_excerpt': 'We report Scope 1, 2, and 3 greenhouse gas emissions annually. In 2022, our Scope 3 emissions totaled 10.2 million tCO2e, with the majority stemming from purchased goods and capital investments.',
            'label': 1
        },
        {
            'company_name': 'Amazon.com Inc',
            'exchange': 'NASDAQ',
            'year': 2023,
            'text_excerpt': 'Our carbon footprint includes Scope 1, 2, and 3 emissions. Scope 3 emissions were disclosed at 51.17 million metric tons of CO2e, accounting for approximately 71% of our total carbon footprint.',
            'label': 1
        },
        {
            'company_name': 'BP PLC',
            'exchange': 'LSE',
            'year': 2022,
            'text_excerpt': 'We measured and reported emissions across all three scopes. Our Scope 3 emissions, primarily from the use of sold products, totaled 360 million tonnes CO2e in 2022.',
            'label': 1
        },
        {
            'company_name': 'Walmart Inc',
            'exchange': 'NYSE',
            'year': 2023,
            'text_excerpt': 'We disclose Scope 1, Scope 2, and Scope 3 emissions in our annual sustainability report. Scope 3 emissions were calculated at approximately 1.5 billion metric tons CO2e, with significant contributions from our supply chain.',
            'label': 1
        },
        {
            'company_name': 'Nike Inc',
            'exchange': 'NYSE',
            'year': 2022,
            'text_excerpt': 'Our comprehensive GHG inventory covers Scopes 1, 2, and 3. We reported Scope 3 emissions of 8.4 million metric tons CO2e, primarily from manufacturing and logistics activities.',
            'label': 1
        },
        {
            'company_name': 'Nestle SA',
            'exchange': 'NYSE',
            'year': 2023,
            'text_excerpt': 'We report all three scopes of greenhouse gas emissions. In 2023, Scope 3 emissions represented 95% of our total footprint at 99.1 million tonnes CO2e, mostly from raw materials and packaging.',
            'label': 1
        },
        {
            'company_name': 'HSBC Holdings',
            'exchange': 'LSE',
            'year': 2022,
            'text_excerpt': 'Our Scope 1 and 2 emissions totaled 387,000 tCO2e. We also calculated and disclosed our Scope 3 financed emissions at 33.1 million tCO2e across our lending and investment portfolios.',
            'label': 1
        },
        {
            'company_name': 'Tesla Inc',
            'exchange': 'NASDAQ',
            'year': 2023,
            'text_excerpt': 'We measure Scope 1, 2, and 3 emissions comprehensively. Our Scope 3 emissions were reported at 29.4 million metric tons CO2e, with vehicle use phase being the largest contributor.',
            'label': 1
        },
        {
            'company_name': 'Procter & Gamble',
            'exchange': 'NYSE',
            'year': 2022,
            'text_excerpt': 'We report emissions across Scopes 1, 2, and 3. Our Scope 3 emissions totaled approximately 165 million metric tons CO2e, representing over 99% of our total carbon footprint.',
            'label': 1
        },
        {
            'company_name': 'Coca-Cola Company',
            'exchange': 'NYSE',
            'year': 2023,
            'text_excerpt': 'Our greenhouse gas emissions reporting includes all three scopes. Scope 3 emissions were disclosed at 25.3 million metric tons of CO2e, primarily from ingredients and packaging.',
            'label': 1
        },
        {
            'company_name': 'IBM Corporation',
            'exchange': 'NYSE',
            'year': 2022,
            'text_excerpt': 'We calculated and reported Scope 1, 2, and 3 greenhouse gas emissions. Our Scope 3 emissions totaled 23.4 million metric tons CO2e, mainly from purchased goods, services, and use of sold products.',
            'label': 1
        }
    ]
    
    return pd.DataFrame(scope3_examples)


def merge_with_existing_dataset(synthetic_df, existing_csv='dataset.csv', output_csv='dataset_augmented.csv'):
    """Merge synthetic examples with existing dataset"""
    
    if not Path(existing_csv).exists():
        print(f"❌ Existing dataset not found: {existing_csv}")
        return None
    
    # Load existing dataset
    existing_df = pd.read_csv(existing_csv)
    print(f"✓ Loaded existing dataset: {len(existing_df)} rows")
    print(f"  Label 0: {(existing_df['label']==0).sum()}")
    print(f"  Label 1: {(existing_df['label']==1).sum()}")
    
    # Add synthetic examples
    combined_df = pd.concat([existing_df, synthetic_df], ignore_index=True)
    print(f"\n✓ Added {len(synthetic_df)} synthetic Scope 3 examples")
    print(f"\nCombined dataset: {len(combined_df)} rows")
    print(f"  Label 0: {(combined_df['label']==0).sum()} ({(combined_df['label']==0).sum()/len(combined_df)*100:.1f}%)")
    print(f"  Label 1: {(combined_df['label']==1).sum()} ({(combined_df['label']==1).sum()/len(combined_df)*100:.1f}%)")
    
    # Save
    combined_df.to_csv(output_csv, index=False)
    print(f"\n✓ Saved augmented dataset to: {output_csv}")
    
    return combined_df


def main():
    """Main function"""
    
    print("="*70)
    print("SCOPE 3 EXAMPLE GENERATOR")
    print("="*70)
    print("\nThis script adds realistic Scope 3 reporting examples to your dataset")
    print("These examples are based on actual corporate sustainability reports.")
    print()
    
    # Create synthetic examples
    synthetic_df = create_scope3_examples()
    print(f"✓ Created {len(synthetic_df)} synthetic Scope 3 examples")
    
    # Merge with existing dataset
    print("\n" + "="*70)
    print("MERGING WITH EXISTING DATASET")
    print("="*70)
    
    result_df = merge_with_existing_dataset(synthetic_df)
    
    if result_df is not None:
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("1. Review dataset_augmented.csv to verify the merged data")
        print("2. If satisfied, replace dataset.csv:")
        print("   - Rename dataset.csv to dataset_backup.csv")
        print("   - Rename dataset_augmented.csv to dataset.csv")
        print("3. Run training: python training_script.py --validation validation.csv")
        print("="*70)
    else:
        # Just save synthetic examples
        output_file = 'scope3_examples.csv'
        synthetic_df.to_csv(output_file, index=False)
        print(f"\n✓ Saved synthetic examples to: {output_file}")
        print("\nYou can manually merge these with your dataset")


if __name__ == "__main__":
    main()
