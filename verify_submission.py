"""Final submission verification"""
import os
import pandas as pd

print("="*70)
print("SUBMISSION FILE VERIFICATION")
print("="*70)

required_files = [
    'scraper_script.py',
    'dataset.csv',
    'training_script.py',
    'requirements.txt',
    'README.md'
]

print("\nRequired Files:")
all_present = True
for f in required_files:
    exists = os.path.exists(f)
    status = "✅" if exists else "❌"
    print(f"{status} {f}")
    all_present = all_present and exists

print("\nDataset Verification:")
df = pd.read_csv('dataset.csv')
print(f"✅ Total rows: {len(df)}")
print(f"✅ Label 0: {(df['label']==0).sum()}")
print(f"✅ Label 1: {(df['label']==1).sum()}")
print(f"✅ Unique companies: {df['company_name'].nunique()}")
print(f"✅ Exchanges: {sorted(df['exchange'].unique().tolist())}")

print("\nModel Directory:")
if os.path.exists('model'):
    model_files = len(os.listdir('model'))
    print(f"✅ Model saved ({model_files} files)")
else:
    print("❌ Model directory not found")

print("\n" + "="*70)
if all_present:
    print("✅ ALL SUBMISSION FILES READY")
else:
    print("❌ SOME FILES MISSING")
print("="*70)
