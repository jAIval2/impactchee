"""
Diagnostic Script: Find Scope 3 Mentions
Helps identify if labeling logic is too strict or data lacks Scope 3 reporting
"""

import os
import re
import pandas as pd
from pathlib import Path


def search_scope3_patterns(text_path):
    """Search for any Scope 3 mentions with different patterns"""
    
    with open(text_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    content_lower = content.lower()
    
    results = {
        'file': text_path,
        'has_scope3_mention': False,
        'scope3_count': 0,
        'patterns_found': [],
        'sample_contexts': []
    }
    
    # Different patterns to search for Scope 3
    patterns = {
        'basic': r'\bscope\s*3\b',
        'roman': r'\bscope\s*iii\b',
        'numeric': r'\bscope\s*three\b',
        'reporting': r'report.*scope\s*3',
        'emissions': r'scope\s*3.*emissions?',
        'value': r'scope\s*3.*\d+',
        'all_three': r'(?:scope\s*1|scope\s*2|scope\s*3).*(?:scope\s*1|scope\s*2|scope\s*3).*(?:scope\s*1|scope\s*2|scope\s*3)'
    }
    
    for pattern_name, pattern in patterns.items():
        matches = list(re.finditer(pattern, content_lower, re.IGNORECASE))
        if matches:
            results['has_scope3_mention'] = True
            results['scope3_count'] += len(matches)
            results['patterns_found'].append(pattern_name)
            
            # Get context around first match
            if matches and len(results['sample_contexts']) < 3:
                match = matches[0]
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end].replace('\n', ' ')
                results['sample_contexts'].append({
                    'pattern': pattern_name,
                    'context': context[:200]
                })
    
    return results


def main():
    """Main diagnostic function"""
    
    print("="*70)
    print("SCOPE 3 DIAGNOSTIC TOOL")
    print("="*70)
    
    texts_dir = Path('data/texts')
    
    if not texts_dir.exists():
        print(f"❌ Directory not found: {texts_dir}")
        return
    
    text_files = list(texts_dir.glob('*.txt'))
    print(f"\nScanning {len(text_files)} text files...\n")
    
    results_list = []
    files_with_scope3 = []
    
    for i, text_file in enumerate(text_files, 1):
        if i % 10 == 0:
            print(f"  Processed {i}/{len(text_files)} files...")
        
        result = search_scope3_patterns(text_file)
        results_list.append(result)
        
        if result['has_scope3_mention']:
            files_with_scope3.append(result)
    
    print(f"\n✓ Scan complete!\n")
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total files scanned: {len(text_files)}")
    print(f"Files with Scope 3 mentions: {len(files_with_scope3)}")
    print(f"Percentage: {len(files_with_scope3)/len(text_files)*100:.1f}%")
    
    if files_with_scope3:
        print("\n" + "="*70)
        print("FILES WITH SCOPE 3 MENTIONS")
        print("="*70)
        
        for i, result in enumerate(files_with_scope3[:10], 1):  # Show first 10
            filename = Path(result['file']).name
            print(f"\n{i}. {filename}")
            print(f"   Patterns found: {', '.join(result['patterns_found'])}")
            print(f"   Mention count: {result['scope3_count']}")
            
            if result['sample_contexts']:
                print(f"   Sample context:")
                for ctx in result['sample_contexts'][:1]:
                    print(f"   → {ctx['context'][:150]}...")
        
        if len(files_with_scope3) > 10:
            print(f"\n... and {len(files_with_scope3) - 10} more files")
        
        # Recommendations
        print("\n" + "="*70)
        print("RECOMMENDATIONS")
        print("="*70)
        print("✓ Scope 3 mentions found in text files!")
        print("\nNext steps:")
        print("1. Review the sample contexts above")
        print("2. Check if these are actual reporting vs. future plans")
        print("3. If labeling logic is too strict, consider:")
        print("   - Relaxing pattern matching in create_dataset.py")
        print("   - Manually reviewing and labeling some excerpts")
        print("   - Adjusting the 'reporting_phrases' regex patterns")
        
    else:
        print("\n" + "="*70)
        print("NO SCOPE 3 MENTIONS FOUND")
        print("="*70)
        print("⚠ The text files don't contain Scope 3 references.")
        print("\nPossible reasons:")
        print("1. Companies scraped are small-cap and don't report Scope 3")
        print("2. PDF text extraction missed relevant sections")
        print("3. Need to target different companies (e.g., S&P 500)")
        print("\nRecommendations:")
        print("1. Re-run scraper targeting larger companies")
        print("2. Look for industries with strong sustainability focus:")
        print("   - Technology (Microsoft, Google, Apple)")
        print("   - Consumer goods (Unilever, P&G)")
        print("   - Financial services (major banks)")
        print("3. Search for sustainability reports instead of annual reports")
    
    # Save detailed results
    output_file = 'scope3_diagnostic_results.csv'
    df = pd.DataFrame([{
        'file': Path(r['file']).name,
        'has_scope3': r['has_scope3_mention'],
        'count': r['scope3_count'],
        'patterns': ','.join(r['patterns_found']) if r['patterns_found'] else 'none'
    } for r in results_list])
    
    df.to_csv(output_file, index=False)
    print(f"\n✓ Detailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
