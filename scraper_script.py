"""
Annual Report Scraper - Practical Approach
Uses direct company URLs from annualreports.com homepage
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin
import pdfplumber
import pandas as pd
from typing import List, Dict, Optional

class AnnualReportScraper:
    """
    Practical scraper - gets companies directly from homepage
    """
    
    def __init__(self, base_url="https://www.annualreports.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Exchange detection
        self.exchange_patterns = {
            'NYSE': [r'nyse[:\s]', r'new york stock'],
            'NASDAQ': [r'nasdaq[:\s]', r'nasd'],
            'LSE': [r'lse[:\s]', r'london stock'],
            'ASX': [r'asx[:\s]', r'australian'],
            'TSX': [r'tsx[:\s]', r'toronto'],
        }
    
    def get_companies_from_homepage(self, limit: int = 5) -> List[Dict]:
        """
        Get companies directly from homepage
        """
        print("Fetching companies from homepage...")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            companies = []
            
            # Find all company links (pattern: /Company/xxx)
            company_links = soup.find_all('a', href=re.compile(r'/Company/[a-zA-Z0-9-]+$'))
            
            seen_urls = set()
            for link in company_links:
                href = link.get('href')
                company_name = link.get_text(strip=True)
                
                # Skip empty names or "View Report" buttons
                if not company_name or company_name.lower() in ['view report', 'view', 'report']:
                    continue
                
                # Only reasonable company names
                if 3 < len(company_name) < 100:
                    company_url = urljoin(self.base_url, href)
                    
                    if company_url not in seen_urls:
                        companies.append({
                            'name': company_name,
                            'url': company_url
                        })
                        seen_urls.add(company_url)
                        print(f"  ✓ Found: {company_name}")
                
                if len(companies) >= limit:
                    break
            
            return companies
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return []
    
    def get_company_details(self, company: Dict) -> Optional[Dict]:
        """
        Get PDFs and exchange info for a company
        """
        print(f"\n  Processing: {company['name']}")
        
        try:
            response = self.session.get(company['url'], timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get better company name from page
            h1 = soup.find('h1')
            company_name = h1.get_text(strip=True) if h1 else company['name']
            print(f"    Company: {company_name}")
            
            # Detect exchange
            exchange = self._detect_exchange(soup)
            print(f"    Exchange: {exchange}")
            
            # Find PDFs
            pdfs = self._find_pdfs(soup, company['url'])
            print(f"    Found {len(pdfs)} PDFs")
            
            if not pdfs:
                return None
            
            return {
                'name': company_name,
                'exchange': exchange,
                'pdfs': pdfs,
                'url': company['url']
            }
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return None
    
    def _detect_exchange(self, soup: BeautifulSoup) -> str:
        """Detect stock exchange from page"""
        page_text = soup.get_text().lower()
        
        for exchange, patterns in self.exchange_patterns.items():
            for pattern in patterns:
                if re.search(pattern, page_text):
                    return exchange
        
        return "NYSE"  # Default
    
    def _find_pdfs(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Find PDF links on page"""
        pdfs = []
        
        # Find all links with .pdf
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link['href'].lower()
            
            # Must be PDF
            if not href.endswith('.pdf'):
                continue
            
            # Skip quarterly/proxy reports
            if any(x in href for x in ['q1', 'q2', 'q3', 'q4', 'quarter', 'proxy', 'def_14a']):
                continue
            
            # Extract year
            year_match = re.search(r'(202[0-5])', href)
            if not year_match:
                continue
            
            year = int(year_match.group(1))
            full_url = urljoin(base_url, link['href'])
            
            # Avoid duplicates
            if not any(p['url'] == full_url for p in pdfs):
                pdfs.append({
                    'url': full_url,
                    'year': year
                })
        
        return pdfs
    
    def download_pdf(self, url: str, company: str, year: int) -> Optional[str]:
        """Download PDF file"""
        
        # Clean filename
        safe_name = re.sub(r'[^\w\s-]', '', company)[:50]
        filename = f"{safe_name}_{year}.pdf"
        filepath = os.path.join("data/pdfs", filename)
        
        # Skip if exists and valid
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"      ✓ Already exists")
            return filepath
        
        try:
            print(f"      Downloading {filename}...")
            
            # Stream download
            with self.session.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            # Verify size
            size = os.path.getsize(filepath)
            if size < 1000:
                os.remove(filepath)
                print(f"      ✗ Too small ({size} bytes)")
                return None
            
            print(f"      ✓ Downloaded ({size:,} bytes)")
            return filepath
            
        except Exception as e:
            print(f"      ✗ Failed: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return None

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF"""
    try:
        print(f"      Extracting text...")
        text = ""
        
        with pdfplumber.open(pdf_path) as pdf:
            # First 50 pages only
            for page in pdf.pages[:50]:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except:
                    pass
        
        if len(text) > 500:
            print(f"      ✓ Extracted {len(text):,} chars")
            return text.strip()
        else:
            print(f"      ✗ Too short ({len(text)} chars)")
            return ""
            
    except Exception as e:
        print(f"      ✗ Error: {e}")
        return ""

def main():
    """Main workflow"""
    
    # Setup
    os.makedirs("data/pdfs", exist_ok=True)
    os.makedirs("data/texts", exist_ok=True)
    
    scraper = AnnualReportScraper()
    
    print("="*70)
    print("ANNUAL REPORT SCRAPER")
    print("="*70)
    
    # Step 1: Get companies
    print("\nSTEP 1: Finding companies...")
    print("-" * 70)
    companies = scraper.get_companies_from_homepage(limit=10)
    
    if not companies:
        print("\n✗ No companies found")
        print("\nTrying manual fallback...")
        companies = [
            {'name': 'Apple', 'url': 'https://www.annualreports.com/Company/apple-inc'},
            {'name': 'Microsoft', 'url': 'https://www.annualreports.com/Company/microsoft-corp'},
            {'name': 'Amazon', 'url': 'https://www.annualreports.com/Company/amazon-com-inc'},
            {'name': 'Tesla', 'url': 'https://www.annualreports.com/Company/tesla-inc'},
            {'name': 'Google', 'url': 'https://www.annualreports.com/Company/alphabet-inc'},
        ]
        print(f"Using {len(companies)} fallback companies")
    
    print(f"\n✓ Have {len(companies)} companies to process")
    
    # Step 2: Get details
    print("\nSTEP 2: Getting company details...")
    print("-" * 70)
    
    all_reports = []
    for i, company in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] {company['name']}")
        details = scraper.get_company_details(company)
        
        if details:
            for pdf in details['pdfs']:
                all_reports.append({
                    'company': details['name'],
                    'exchange': details['exchange'],
                    'year': pdf['year'],
                    'url': pdf['url']
                })
        
        time.sleep(2)
    
    print(f"\n✓ Found {len(all_reports)} reports")
    
    if not all_reports:
        print("\n✗ No reports found. Website may have changed or require authentication.")
        return
    
    # Step 3: Download
    print("\nSTEP 3: Downloading PDFs...")
    print("-" * 70)
    
    downloaded = []
    for i, report in enumerate(all_reports, 1):
        print(f"  [{i}/{len(all_reports)}] {report['company']} ({report['year']})")
        
        filepath = scraper.download_pdf(
            report['url'],
            report['company'],
            report['year']
        )
        
        if filepath:
            downloaded.append({
                **report,
                'pdf_path': filepath
            })
        
        time.sleep(1)
    
    print(f"\n✓ Downloaded {len(downloaded)} PDFs")
    
    if not downloaded:
        print("\n✗ No PDFs downloaded")
        return
    
    # Step 4: Extract text
    print("\nSTEP 4: Extracting text...")
    print("-" * 70)
    
    final_data = []
    for i, item in enumerate(downloaded, 1):
        print(f"  [{i}/{len(downloaded)}] {item['company']} ({item['year']})")
        
        text = extract_text_from_pdf(item['pdf_path'])
        
        if text:
            # Save text file
            safe_name = re.sub(r'[^\w\s-]', '', item['company'])[:50]
            text_file = f"{safe_name}_{item['year']}.txt"
            text_path = os.path.join("data/texts", text_file)
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            final_data.append({
                'company': item['company'],
                'exchange': item['exchange'],
                'year': item['year'],
                'pdf_path': item['pdf_path'],
                'text_path': text_path,
                'text': text
            })
    
    # Summary
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    if final_data:
        print(f"✓ Successfully processed: {len(final_data)} reports")
        print(f"✓ Companies: {len(set(d['company'] for d in final_data))}")
        print(f"✓ Exchanges: {sorted(set(d['exchange'] for d in final_data))}")
        print(f"✓ Years: {sorted(set(d['year'] for d in final_data))}")
        
        # Save metadata
        df = pd.DataFrame([{
            'company': d['company'],
            'exchange': d['exchange'],
            'year': d['year'],
            'pdf_path': d['pdf_path'],
            'text_path': d['text_path']
        } for d in final_data])
        
        df.to_csv('data/pdf_metadata.csv', index=False)
        print(f"\n✓ Saved metadata to data/pdf_metadata.csv")
        print("\n" + "="*70)
        print("NEXT: Create labeled dataset with create_dataset.py")
        print("="*70)
    else:
        print("✗ No data processed successfully")
    
    return final_data

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
