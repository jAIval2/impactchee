"""
Dataset Creation Script
Extracts and labels text excerpts from annual reports for Scope 1, 2, 3 emissions
"""

import pandas as pd
import re
import os
from typing import List, Dict, Optional

class DatasetCreator:
    """Creates labeled dataset from extracted texts"""
    
    def __init__(self):
        # Patterns to find scope mentions
        self.scope_patterns = {
            'scope_1': r'\bscope\s*[1I](?:\s+emissions?|\s+ghg|\b|\s*[,&-])',
            'scope_2': r'\bscope\s*[2II](?:\s+emissions?|\s+ghg|\b|\s*[,&-])',
            'scope_3': r'\bscope\s*[3III](?:\s+emissions?|\s+ghg|\b|\s*[,&-])'
        }
        
        # Additional patterns for better scope detection
        self.scope_combined_patterns = [
            r'\bscopes?\s*[1I][-,]?[2II](?:[-,]\s*and\s*|\s*[&,]\s*)[3III]\b',
            r'all\s+three\s+scopes?\b',
            r'\bscopes?\s*[1I][-,][3III]\b',
            r'\bcarbon\s+footprint.*scope\s*[3III]',
            r'\bghg\s+emissions.*scope\s*[3III]'
        ]
    
    def find_scope_excerpts(self, text: str) -> List[Dict]:
        """
        Find excerpts that specifically mention scope reporting
        Returns excerpts with label information
        """
        text_lower = text.lower()
        excerpts = []
        
        # Split into lines first
        lines = text.split('\n')
        
        # Find all lines that mention "scope"
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            
            # Must mention "scope" to be relevant
            if 'scope' not in line_lower:
                continue
            
            # Build context: take current line + surrounding lines to form a chunk
            # This helps capture table data spread across multiple lines
            start_idx = max(0, idx - 3)  # 3 lines before
            end_idx = min(len(lines), idx + 4)  # 3 lines after
            
            # Combine lines into a paragraph with context
            paragraph = ' '.join(lines[start_idx:end_idx])
            para_lower = paragraph.lower()
            
            # Skip if too short after combining
            if len(paragraph.strip()) < 100:
                continue
            
            # Check what scopes are mentioned in this context
            has_scope_1 = bool(re.search(self.scope_patterns['scope_1'], para_lower))
            has_scope_2 = bool(re.search(self.scope_patterns['scope_2'], para_lower))
            has_scope_3 = bool(re.search(self.scope_patterns['scope_3'], para_lower))
            
            # Must mention at least scope 1 or 2
            if not (has_scope_1 or has_scope_2):
                continue
            
            # Determine label for this excerpt
            label = self.determine_label_for_excerpt(paragraph)
            
            # Create excerpt (limit to 500 chars as per requirements)
            excerpt = paragraph.strip()[:500]
            
            # Only add if it has meaningful content and not duplicate
            if len(excerpt) > 50:
                # Check if similar excerpt already exists (avoid duplicates from overlapping context)
                is_duplicate = any(
                    excerpt[:200] == existing['text'][:200] 
                    for existing in excerpts
                )
                
                if not is_duplicate:
                    excerpts.append({
                        'text': excerpt,
                        'label': label,
                        'has_scope_1': has_scope_1,
                        'has_scope_2': has_scope_2,
                        'has_scope_3': has_scope_3
                    })
        
        return excerpts
    
    def determine_label_for_excerpt(self, text: str) -> int:
        """
        Determine if excerpt explicitly reports Scope 3
        
        Label 1: Explicitly mentions reporting Scope 3 (e.g., "we report Scope 1, 2, and 3")
        Label 0: Only mentions Scope 1 and/or 2, OR mentions Scope 3 as future plan
        """
        text_lower = text.lower()
        
        # Check if Scope 3 is mentioned
        has_scope_3 = bool(re.search(self.scope_patterns['scope_3'], text_lower))
        
        if not has_scope_3:
            return 0
        
        # Check if it's actual reporting (not future plans)
        # Indicators of ACTUAL reporting
        reporting_phrases = [
            # Direct reporting statements
            r'report(?:ed|s|ing)?\s+(?:our\s+)?scope\s*3',
            r'scope\s*3\s+emissions?\s+(?:are|were|totaled?|amount(?:ed)?)',
            r'scope\s*3\s+emissions?\s+(?:of|:)?\s*[0-9]',
            r'(?:measured|calculated|disclosed?|assess(?:ed)?|monitor(?:ed)?)\s+(?:our\s+)?scope\s*3',
            
            # Combined scope reporting
            r'scope\s*[1I],?\s*[2II],?\s*(?:and|&)\s*[3III]',
            r'scope\s*[1I],?\s*[2II]\s*(?:and|&)\s*[3III]\s+emissions?',
            r'all\s+three\s+scopes?',
            r'scopes?\s*[1I][-,][3III]',
            
            # Quantitative indicators (relaxed to catch table data)
            r'scope\s*3.*\d+[,\d]*\s*(?:tonnes?|tco2e?|mtco2e?|kt|mt)',
            r'\d+[,\d]*\s*(?:tonnes?|tco2e?|mtco2e?|kt|mt).*scope\s*3',  # Number before Scope 3
            r'scope\s*3.*carbon',
            r'total.*scope\s*3.*emissions?.*\d+',
            r'scope\s*3.*total.*\d+',
            
            # Additional reporting contexts
            r'scope\s*3.*footprint',
            r'scope\s*3.*inventory',
            r'scope\s*3.*(?:emissions?\s+)?data',
            r'scope\s*3.*metrics?',
            r'scope\s*3.*performance',
            r'scope\s*3.*results?',
            r'scope\s*3\s+category',  # Scope 3 category breakdown
            r'scope\s*3\s+emissions?\s+table',
            r'ghg.*scope\s*3',
            r'scope\s*3.*ghg',
        ]
        
        # Indicators of FUTURE PLANS (should be labeled 0)
        future_phrases = [
            r'(?:will|plan|intend|aim|target|goal|future|upcoming|next year).*scope\s*3',
            r'scope\s*3.*(?:in\s+)?(?:202[6-9]|203[0-9])',  # Future years
            r'scope\s*3.*(?:by|until)\s+202[6-9]',
            r'begin.*report.*scope\s*3',
            r'start.*scope\s*3',
            r'working\s+(?:on|toward).*scope\s*3',
            r'develop.*scope\s*3',
            r'currently\s+do\s+not.*scope\s*3',
            r'(?:in\s+the\s+)?process\s+of\s+calculating.*scope\s*3',
            r'to\s+calculate.*scope\s*3',
            r'not\s+yet.*scope\s*3',
        ]
        
        # Check for actual reporting
        is_reporting = any(re.search(pattern, text_lower) for pattern in reporting_phrases)
        is_future = any(re.search(pattern, text_lower) for pattern in future_phrases)
        
        # Label as 1 only if reporting AND not future plan
        if is_reporting and not is_future:
            return 1
        
        return 0
    
    def create_dataset(self, metadata_csv: str = 'data/pdf_metadata.csv') -> pd.DataFrame:
        """
        Main function to create labeled dataset
        """
        print("Creating labeled dataset...")
        print("-" * 70)
        
        # Load metadata
        if not os.path.exists(metadata_csv):
            print(f"✗ Metadata file not found: {metadata_csv}")
            return pd.DataFrame()
        
        metadata = pd.read_csv(metadata_csv)
        print(f"✓ Loaded {len(metadata)} reports")
        
        dataset_rows = []
        
        for idx, row in metadata.iterrows():
            company = row['company']
            exchange = row['exchange']
            year = row['year']
            text_path = row['text_path']
            
            print(f"\n[{idx+1}/{len(metadata)}] Processing: {company} ({year})")
            
            # Load text
            if not os.path.exists(text_path):
                print(f"  ✗ Text file not found: {text_path}")
                continue
            
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Find scope-related excerpts
            excerpts = self.find_scope_excerpts(text)
            print(f"  Found {len(excerpts)} scope-related excerpts")
            
            if not excerpts:
                # If no scope excerpts found, create a generic one with label 0
                print(f"  ⚠ No scope mentions found - creating generic excerpt")
                # Try to find any emissions-related text
                generic_text = self._find_generic_excerpt(text)
                if generic_text:
                    dataset_rows.append({
                        'company_name': company,
                        'exchange': exchange,
                        'year': year,
                        'text_excerpt': generic_text,
                        'label': 0
                    })
                continue
            
            # Take up to 3 excerpts per report to ensure diversity
            for i, excerpt_data in enumerate(excerpts[:3]):
                excerpt_text = excerpt_data['text']
                label = excerpt_data['label']
                
                dataset_rows.append({
                    'company_name': company,
                    'exchange': exchange,
                    'year': year,
                    'text_excerpt': excerpt_text,
                    'label': label
                })
                
                scope_info = []
                if excerpt_data['has_scope_1']: scope_info.append('S1')
                if excerpt_data['has_scope_2']: scope_info.append('S2')
                if excerpt_data['has_scope_3']: scope_info.append('S3')
                
                print(f"    Excerpt {i+1}: Label={label}, Scopes={','.join(scope_info)}, Length={len(excerpt_text)}")
        
        # Create DataFrame
        df = pd.DataFrame(dataset_rows)
        
        if df.empty:
            print("\n✗ No excerpts created")
            return df
        
        print("\n" + "="*70)
        print("DATASET SUMMARY")
        print("="*70)
        print(f"Total excerpts: {len(df)}")
        print(f"Unique companies: {df['company_name'].nunique()}")
        print(f"Exchanges: {sorted(df['exchange'].unique().tolist())}")
        print(f"Years: {sorted(df['year'].unique().tolist())}")
        print(f"\nLabel distribution:")
        print(df['label'].value_counts().to_string())
        print(f"\nLabel 0 (Scope 1&2 only): {(df['label']==0).sum()} ({(df['label']==0).sum()/len(df)*100:.1f}%)")
        print(f"Label 1 (Scope 1,2,3): {(df['label']==1).sum()} ({(df['label']==1).sum()/len(df)*100:.1f}%)")
        
        # Warning if imbalanced
        if (df['label']==1).sum() == 0:
            print("\n⚠ WARNING: No Scope 3 reporting found (all labels are 0)")
            print("  This may indicate:")
            print("  - Companies in dataset don't report Scope 3")
            print("  - Labeling logic is too strict")
            print("  - Need more diverse company sample")
        
        return df
    
    def _find_generic_excerpt(self, text: str) -> Optional[str]:
        """Find any emissions-related text as fallback"""
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            para_lower = paragraph.lower()
            if any(kw in para_lower for kw in ['emission', 'carbon', 'ghg', 'greenhouse gas', 'climate']):
                if len(paragraph.strip()) > 100:
                    return paragraph.strip()[:500]
        
        return None
    
    def save_dataset(self, df: pd.DataFrame, output_path: str = 'dataset.csv'):
        """Save dataset to CSV with exact required format"""
        if df.empty:
            print("\n✗ No data to save")
            return
        
        # Ensure correct column order and names as per requirements
        required_columns = ['company_name', 'exchange', 'year', 'text_excerpt', 'label']
        df = df[required_columns]
        
        # Validate data
        print("\n" + "="*70)
        print("VALIDATION")
        print("="*70)
        print(f"✓ Column names: {list(df.columns)}")
        print(f"✓ Total rows: {len(df)}")
        print(f"✓ No missing values: {df.isnull().sum().sum() == 0}")
        print(f"✓ Text excerpt lengths: {df['text_excerpt'].str.len().min()}-{df['text_excerpt'].str.len().max()} chars")
        print(f"✓ Max excerpt length <= 500: {df['text_excerpt'].str.len().max() <= 500}")
        
        # Save
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved dataset to: {output_path}")
        
        # Show sample
        print("\n" + "="*70)
        print("SAMPLE ROWS")
        print("="*70)
        sample = df.head(3)
        for idx, row in sample.iterrows():
            print(f"\nRow {idx+1}:")
            print(f"  Company: {row['company_name']}")
            print(f"  Exchange: {row['exchange']}")
            print(f"  Year: {row['year']}")
            print(f"  Label: {row['label']}")
            print(f"  Excerpt: {row['text_excerpt'][:100]}...")

def main():
    """Main execution"""
    
    print("="*70)
    print("DATASET CREATION - Scope 1, 2, 3 Labeling")
    print("="*70)
    
    creator = DatasetCreator()
    
    # Create dataset
    df = creator.create_dataset()
    
    if not df.empty:
        # Save dataset
        creator.save_dataset(df, 'dataset.csv')
        
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("1. Review dataset.csv to verify labels are correct")
        print("2. Check some excerpts manually:")
        print("   - Label 1 should explicitly report Scope 3")
        print("   - Label 0 should only report Scope 1&2 or mention future Scope 3 plans")
        print("3. If labels look wrong, you can manually edit dataset.csv")
        print("4. Once satisfied, run: python training_script.py --validation validation.csv")
        print("="*70)
    else:
        print("\n✗ Failed to create dataset")
        print("\nPossible issues:")
        print("  - No text files found")
        print("  - Text files don't contain scope/emissions mentions")
        print("  - Check that data/pdf_metadata.csv exists and paths are correct")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
