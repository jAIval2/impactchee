"""
Annual Report Scraper - Hybrid Approach
Dynamically parses annualreports.com with fallback database
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin
import pdfplumber
import pandas as pd
import random
from typing import List, Dict, Optional

class AnnualReportScraper:
    """
    Hybrid scraper: Dynamic URL parsing + fallback database
    """
    
    def __init__(self, base_url="https://www.annualreports.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Exchange detection patterns
        self.exchange_patterns = {
            'NYSE': [r'nyse[:\s]', r'new york stock'],
            'NASDAQ': [r'nasdaq[:\s]', r'nasd'],
            'LSE': [r'lse[:\s]', r'london stock'],
            'ASX': [r'asx[:\s]', r'australian'],
            'TSX': [r'tsx[:\s]', r'toronto'],
        }
        
        # Fallback company database (used if dynamic scraping fails)
        self.company_database = [
            # Tech - NASDAQ
            {'name': 'Apple Inc.', 'url': f'{base_url}/Company/apple-inc', 'exchange': 'NASDAQ'},
            {'name': 'Microsoft Corporation', 'url': f'{base_url}/Company/microsoft-corp', 'exchange': 'NASDAQ'},
            {'name': 'Alphabet Inc.', 'url': f'{base_url}/Company/alphabet-inc', 'exchange': 'NASDAQ'},
            {'name': 'Amazon.com Inc.', 'url': f'{base_url}/Company/amazon-com-inc', 'exchange': 'NASDAQ'},
            {'name': 'Meta Platforms Inc.', 'url': f'{base_url}/Company/meta-platforms-inc', 'exchange': 'NASDAQ'},
            {'name': 'Tesla Inc.', 'url': f'{base_url}/Company/tesla-inc', 'exchange': 'NASDAQ'},
            {'name': 'NVIDIA Corporation', 'url': f'{base_url}/Company/nvidia-corp', 'exchange': 'NASDAQ'},
            {'name': 'Intel Corporation', 'url': f'{base_url}/Company/intel-corp', 'exchange': 'NASDAQ'},
            {'name': 'Adobe Inc.', 'url': f'{base_url}/Company/adobe-inc', 'exchange': 'NASDAQ'},
            {'name': 'Cisco Systems Inc.', 'url': f'{base_url}/Company/cisco-systems-inc', 'exchange': 'NASDAQ'},
            {'name': 'Oracle Corporation', 'url': f'{base_url}/Company/oracle-corp', 'exchange': 'NASDAQ'},
            {'name': 'Salesforce Inc.', 'url': f'{base_url}/Company/salesforce-inc', 'exchange': 'NASDAQ'},
            {'name': 'Netflix Inc.', 'url': f'{base_url}/Company/netflix-inc', 'exchange': 'NASDAQ'},
            {'name': 'PayPal Holdings Inc.', 'url': f'{base_url}/Company/paypal-holdings-inc', 'exchange': 'NASDAQ'},
            {'name': 'Qualcomm Inc.', 'url': f'{base_url}/Company/qualcomm-inc', 'exchange': 'NASDAQ'},
            
            # Finance - NYSE
            {'name': 'JPMorgan Chase & Co.', 'url': f'{base_url}/Company/jpmorgan-chase-co', 'exchange': 'NYSE'},
            {'name': 'Bank of America Corp.', 'url': f'{base_url}/Company/bank-of-america-corp', 'exchange': 'NYSE'},
            {'name': 'Wells Fargo & Company', 'url': f'{base_url}/Company/wells-fargo-company', 'exchange': 'NYSE'},
            {'name': 'Citigroup Inc.', 'url': f'{base_url}/Company/citigroup-inc', 'exchange': 'NYSE'},
            {'name': 'Goldman Sachs Group Inc.', 'url': f'{base_url}/Company/goldman-sachs-group-inc', 'exchange': 'NYSE'},
            {'name': 'Morgan Stanley', 'url': f'{base_url}/Company/morgan-stanley', 'exchange': 'NYSE'},
            {'name': 'American Express Company', 'url': f'{base_url}/Company/american-express-company', 'exchange': 'NYSE'},
            {'name': 'Visa Inc.', 'url': f'{base_url}/Company/visa-inc', 'exchange': 'NYSE'},
            {'name': 'Mastercard Inc.', 'url': f'{base_url}/Company/mastercard-inc', 'exchange': 'NYSE'},
            
            # Energy - NYSE
            {'name': 'Exxon Mobil Corporation', 'url': f'{base_url}/Company/exxon-mobil-corp', 'exchange': 'NYSE'},
            {'name': 'Chevron Corporation', 'url': f'{base_url}/Company/chevron-corp', 'exchange': 'NYSE'},
            {'name': 'ConocoPhillips', 'url': f'{base_url}/Company/conocophillips', 'exchange': 'NYSE'},
            {'name': 'NextEra Energy Inc.', 'url': f'{base_url}/Company/nextera-energy-inc', 'exchange': 'NYSE'},
            {'name': 'Duke Energy Corporation', 'url': f'{base_url}/Company/duke-energy-corp', 'exchange': 'NYSE'},
            
            # Healthcare - NYSE
            {'name': 'Johnson & Johnson', 'url': f'{base_url}/Company/johnson-johnson', 'exchange': 'NYSE'},
            {'name': 'UnitedHealth Group Inc.', 'url': f'{base_url}/Company/unitedhealth-group-inc', 'exchange': 'NYSE'},
            {'name': 'Pfizer Inc.', 'url': f'{base_url}/Company/pfizer-inc', 'exchange': 'NYSE'},
            {'name': 'Abbott Laboratories', 'url': f'{base_url}/Company/abbott-laboratories', 'exchange': 'NYSE'},
            {'name': 'Merck & Co. Inc.', 'url': f'{base_url}/Company/merck-co-inc', 'exchange': 'NYSE'},
            {'name': 'AbbVie Inc.', 'url': f'{base_url}/Company/abbvie-inc', 'exchange': 'NYSE'},
            
            # Consumer - NYSE
            {'name': 'Procter & Gamble Company', 'url': f'{base_url}/Company/procter-gamble-company', 'exchange': 'NYSE'},
            {'name': 'Coca-Cola Company', 'url': f'{base_url}/Company/coca-cola-company', 'exchange': 'NYSE'},
            {'name': 'PepsiCo Inc.', 'url': f'{base_url}/Company/pepsico-inc', 'exchange': 'NASDAQ'},
            {'name': 'Nike Inc.', 'url': f'{base_url}/Company/nike-inc', 'exchange': 'NYSE'},
            {'name': 'McDonald\'s Corporation', 'url': f'{base_url}/Company/mcdonalds-corp', 'exchange': 'NYSE'},
            {'name': 'Walmart Inc.', 'url': f'{base_url}/Company/walmart-inc', 'exchange': 'NYSE'},
            {'name': 'Home Depot Inc.', 'url': f'{base_url}/Company/home-depot-inc', 'exchange': 'NYSE'},
            {'name': 'Target Corporation', 'url': f'{base_url}/Company/target-corp', 'exchange': 'NYSE'},
            
            # Industrial - NYSE
            {'name': '3M Company', 'url': f'{base_url}/Company/3m-company', 'exchange': 'NYSE'},
            {'name': 'General Electric Company', 'url': f'{base_url}/Company/general-electric-company', 'exchange': 'NYSE'},
            {'name': 'Honeywell International Inc.', 'url': f'{base_url}/Company/honeywell-international-inc', 'exchange': 'NASDAQ'},
            {'name': 'Caterpillar Inc.', 'url': f'{base_url}/Company/caterpillar-inc', 'exchange': 'NYSE'},
            {'name': 'Boeing Company', 'url': f'{base_url}/Company/boeing-company', 'exchange': 'NYSE'},
            {'name': 'Lockheed Martin Corporation', 'url': f'{base_url}/Company/lockheed-martin-corp', 'exchange': 'NYSE'},
            
            # Additional diverse companies
            {'name': 'AT&T Inc.', 'url': f'{base_url}/Company/att-inc', 'exchange': 'NYSE'},
            {'name': 'Verizon Communications Inc.', 'url': f'{base_url}/Company/verizon-communications-inc', 'exchange': 'NYSE'},
            {'name': 'Comcast Corporation', 'url': f'{base_url}/Company/comcast-corp', 'exchange': 'NASDAQ'},
            {'name': 'Walt Disney Company', 'url': f'{base_url}/Company/walt-disney-company', 'exchange': 'NYSE'},
            {'name': 'IBM Corporation', 'url': f'{base_url}/Company/ibm-corp', 'exchange': 'NYSE'},
        ]
    
    def get_company_links(self, search_url=None, min_companies=50):
        """
        Dynamically extract company links from annualreports.com
        Falls back to database if scraping fails
        """
        if not search_url:
            search_url = f"{self.base_url}/Companies"
        
        print(f"Step 1: Scraping company links from {search_url}...")
        companies = []
        seen_urls = set()
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple selector strategies for finding company links
            selectors = [
                'a[href*="/Company/"]',
                '.company-name a',
                '.list-unstyled a',
                'table tbody tr td:first-child a'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and '/Company/' in href:
                        full_url = urljoin(self.base_url, href)
                        company_name = link.get_text(strip=True)
                        
                        if company_name and len(company_name) > 3 and full_url not in seen_urls:
                            companies.append({
                                'name': company_name,
                                'url': full_url
                            })
                            seen_urls.add(full_url)
                            print(f"  ✓ Found: {company_name}")
                
                if len(companies) >= min_companies:
                    break
            
            # Generic fallback: find all links with /Company/
            if len(companies) < 20:
                print("  Trying generic link extraction...")
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href')
                    if href and '/Company/' in href and len(href) > 10:
                        full_url = urljoin(self.base_url, href)
                        company_name = link.get_text(strip=True) or "Unknown Company"
                        
                        if full_url not in seen_urls and len(company_name) > 3:
                            companies.append({
                                'name': company_name,
                                'url': full_url
                            })
                            seen_urls.add(full_url)
            
            print(f"\n✓ Dynamically discovered: {len(companies)} companies")
            
        except Exception as e:
            print(f"  ✗ Error scraping website: {e}")
            companies = []
        
        # Fallback to database if not enough companies found
        if len(companies) < min_companies:
            print(f"\n  Need more companies ({len(companies)}/{min_companies})...")
            print(f"  Using fallback database ({len(self.company_database)} companies)")
            
            for company_data in self.company_database:
                if len(companies) >= min_companies:
                    break
                
                company_url = company_data['url']
                if company_url not in seen_urls:
                    companies.append({
                        'name': company_data['name'],
                        'url': company_url
                    })
                    seen_urls.add(company_url)
                    print(f"  ✓ Added from database: {company_data['name']}")
        
        print(f"\n✓ Total companies: {len(companies)}")
        return companies[:min_companies]
    
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
    
    def is_annual_report_link(self, text, href):
        """Check if link appears to be an annual report"""
        ar_indicators = ['annual', 'report', 'ar', '10-k', 'financial', 'statements']
        href_lower = href.lower()
        
        # Check if it's likely an annual report
        has_indicator = any(indicator in text for indicator in ar_indicators)
        has_pdf = '.pdf' in href_lower
        
        # Skip quarterly and proxy reports
        skip_keywords = ['q1', 'q2', 'q3', 'q4', 'quarter', 'quarterly', 'proxy', 'def_14a', 'def-14a']
        is_quarterly = any(kw in text or kw in href_lower for kw in skip_keywords)
        
        return has_pdf and (has_indicator or len(text) > 0) and not is_quarterly
    
    def extract_year(self, text, href):
        """Extract year from text or URL (2020-2025)"""
        year_pattern = r'(202[0-5])'
        
        # Search in text first
        text_match = re.search(year_pattern, text)
        if text_match:
            return int(text_match.group(1))
        
        # Search in URL
        href_match = re.search(year_pattern, href)
        if href_match:
            return int(href_match.group(1))
        
        return None
    
    def _find_pdfs(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Find PDF links on page with improved detection"""
        pdfs = []
        
        # Find all PDF links
        pdf_elements = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
        
        for element in pdf_elements:
            href = element.get('href')
            text = element.get_text(strip=True).lower()
            
            # Check if it's an annual report
            if not self.is_annual_report_link(text, href):
                continue
            
            # Extract year
            year = self.extract_year(text, href)
            if not year or year < 2020 or year > 2025:
                continue
            
            full_url = urljoin(base_url, href)
            
            # Avoid duplicates
            if not any(p['url'] == full_url for p in pdfs):
                pdfs.append({
                    'url': full_url,
                    'year': year
                })
        
        # Also check for iframe embedded PDFs
        iframes = soup.find_all('iframe', src=re.compile(r'\.pdf$', re.I))
        for iframe in iframes:
            src = iframe.get('src')
            if src:
                full_url = urljoin(base_url, src)
                year = self.extract_year("", src)
                if year and 2020 <= year <= 2025:
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
    """Main workflow - Dynamic scraping with fallback"""
    
    # Setup
    os.makedirs("data/pdfs", exist_ok=True)
    os.makedirs("data/texts", exist_ok=True)
    
    scraper = AnnualReportScraper()
    
    print("="*70)
    print("ANNUAL REPORT SCRAPER - Hybrid Dynamic/Database Approach")
    print("="*70)
    
    # Step 1: Get companies (dynamic scraping + fallback database)
    print("\n" + "="*70)
    companies = scraper.get_company_links(min_companies=50)
    print("="*70)
    
    if len(companies) < 50:
        print(f"\n⚠ WARNING: Only found {len(companies)} companies (target: 50)")
        print("Continuing with available companies...")
    
    print(f"\n✓ Ready to process {len(companies)} companies")
    
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
