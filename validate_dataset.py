"""Quick dataset validation script"""
import pandas as pd
import sys

try:
    df = pd.read_csv('dataset.csv')
    
    print("="*70)
    print("DATASET VALIDATION")
    print("="*70)
    
    # Check structure
    print(f"\n✓ Rows: {len(df)}")
    print(f"✓ Columns: {list(df.columns)}")
    
    # Check required columns
    required_cols = ['company_name', 'exchange', 'year', 'text_excerpt', 'label']
    if list(df.columns) == required_cols:
        print("✓ Column names correct")
    else:
        print("✗ Column names incorrect")
        sys.exit(1)
    
    # Check labels
    print(f"\n✓ Label 0: {(df['label']==0).sum()}")
    print(f"✓ Label 1: {(df['label']==1).sum()}")
    
    if (df['label']==1).sum() == 0:
        print("✗ ERROR: No label 1 examples found!")
        sys.exit(1)
    
    # Check data quality
    print(f"\n✓ Missing values: {df.isnull().sum().sum()}")
    print(f"✓ Text excerpt length range: {df['text_excerpt'].str.len().min()}-{df['text_excerpt'].str.len().max()} chars")
    
    if df['text_excerpt'].str.len().max() > 500:
        print("✗ ERROR: Some excerpts exceed 500 characters")
        sys.exit(1)
    
    # Check diversity
    print(f"\n✓ Unique companies: {df['company_name'].nunique()}")
    print(f"✓ Exchanges: {sorted(df['exchange'].unique().tolist())}")
    print(f"✓ Years: {sorted(df['year'].unique().tolist())}")
    
    if df['company_name'].nunique() < 10:
        print("⚠ WARNING: Less than 10 unique companies")
    
    print("\n" + "="*70)
    print("✓ ALL VALIDATIONS PASSED - Ready for training")
    print("="*70)
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)
