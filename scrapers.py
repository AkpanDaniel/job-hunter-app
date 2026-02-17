import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

# Upwork RSS Feed Scraper (Free, no login needed)
def scrape_upwork():
    """Scrape Upwork RSS feeds for community manager jobs"""
    jobs = []
    
    # Upwork RSS feed URLs for different keywords
    feeds = [
        "https://www.upwork.com/ab/feed/jobs/rss?q=discord+manager&sort=recency&paging=0%3B10",
        "https://www.upwork.com/ab/feed/jobs/rss?q=community+manager&sort=recency&paging=0%3B10",
        "https://www.upwork.com/ab/feed/jobs/rss?q=web3+community&sort=recency&paging=0%3B10",
    ]
    
    for feed_url in feeds:
        try:
            response = requests.get(feed_url, timeout=15)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            for item in items[:5]:  # Limit to 5 per feed
                try:
                    title = item.find('title').text
                    link = item.find('link').text
                    description = item.find('description').text if item.find('description') else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') else "Unknown"
                    
                    # Extract job ID from link
                    job_id_match = re.search(r'/jobs/[~]?(\w+)', link)
                    job_id = f"upwork_{job_id_match.group(1)}" if job_id_match else f"upwork_{hash(link) % 1000000}"
                    
                    # Try to extract rate from description
                    rate = "Not specified"
                    rate_match = re.search(r'\$(\d+)\.?\d*\s*-?\s*\$?(\d+)?\.?\d*/hr', description)
                    if rate_match:
                        rate = f"${rate_match.group(1)}-${rate_match.group(2) if rate_match.group(2) else rate_match.group(1)}/hr"
                    
                    # Check for payment verification (Upwork RSS sometimes includes this)
                    client_verified = "payment verified" in description.lower()
                    
                    jobs.append({
                        'id': job_id,
                        'title': title,
                        'platform': 'Upwork',
                        'url': link,
                        'description': description[:500],
                        'rate': rate,
                        'client_verified': client_verified,
                        'client_spent': 'Unknown',
                        'proposals': 0,
                        'posted_date': pub_date
                    })
                except Exception as e:
                    print(f"Error parsing Upwork item: {e}")
                    continue
            
            time.sleep(2)  # Be polite
            
        except Exception as e:
            print(f"Error fetching Upwork feed: {e}")
            continue
    
    print(f"Found {len(jobs)} jobs from Upwork")
    return jobs

# We Work Remotely Scraper
def scrape_weworkremotely():
    """Scrape We Work Remotely for community manager jobs"""
    jobs = []
    
    categories = [
        "https://weworkremotely.com/remote-jobs/search?term=community+manager",
        "https://weworkremotely.com/remote-jobs/search?term=discord",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in categories:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_listings = soup.find_all('li', class_='feature')[:10]  # Limit to 10
            
            for listing in job_listings:
                try:
                    title_elem = listing.find('span', class_='title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    link_elem = listing.find('a')
                    if not link_elem:
                        continue
                    
                    link = "https://weworkremotely.com" + link_elem['href']
                    
                    company_elem = listing.find('span', class_='company')
                    company = company_elem.text.strip() if company_elem else "Unknown"
                    
                    # Extract job ID from URL
                    job_id_match = re.search(r'/(\d+)-', link)
                    job_id = f"wwr_{job_id_match.group(1)}" if job_id_match else f"wwr_{hash(link) % 1000000}"
                    
                    jobs.append({
                        'id': job_id,
                        'title': title,
                        'platform': 'We Work Remotely',
                        'url': link,
                        'description': f"{title} at {company}",
                        'rate': 'See job posting',
                        'client_verified': True,  # WWR vets companies
                        'client_spent': 'N/A',
                        'proposals': 0,
                        'posted_date': datetime.now().strftime('%Y-%m-%d')
                    })
                except Exception as e:
                    print(f"Error parsing WWR listing: {e}")
                    continue
            
            time.sleep(2)
            
        except Exception as e:
            print(f"Error fetching WWR: {e}")
            continue
    
    print(f"Found {len(jobs)} jobs from We Work Remotely")
    return jobs

# CryptoJobsList Scraper  
def scrape_cryptojobs():
    """Scrape CryptoJobsList for Web3 community manager jobs"""
    jobs = []
    
    urls = [
        "https://cryptojobslist.com/community-manager",
        "https://cryptojobslist.com/discord",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='job-list-item')[:10]
            
            for card in job_cards:
                try:
                    title_elem = card.find('h2') or card.find('h3')
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    link_elem = card.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    link = link_elem['href']
                    if not link.startswith('http'):
                        link = "https://cryptojobslist.com" + link
                    
                    # Extract company
                    company_elem = card.find('span', class_='company-name') or card.find('div', class_='company')
                    company = company_elem.text.strip() if company_elem else "Unknown"
                    
                    # Extract salary if available
                    salary_elem = card.find('span', class_='salary')
                    rate = salary_elem.text.strip() if salary_elem else "See posting"
                    
                    job_id = f"crypto_{hash(link) % 1000000}"
                    
                    jobs.append({
                        'id': job_id,
                        'title': title,
                        'platform': 'CryptoJobsList',
                        'url': link,
                        'description': f"{title} at {company}",
                        'rate': rate,
                        'client_verified': True,  # CryptoJobsList vets postings
                        'client_spent': 'N/A',
                        'proposals': 0,
                        'posted_date': datetime.now().strftime('%Y-%m-%d')
                    })
                except Exception as e:
                    print(f"Error parsing CryptoJobs card: {e}")
                    continue
            
            time.sleep(2)
            
        except Exception as e:
            print(f"Error fetching CryptoJobs: {e}")
            continue
    
    print(f"Found {len(jobs)} jobs from CryptoJobsList")
    return jobs

# Test function
if __name__ == "__main__":
    print("Testing scrapers...")
    
    print("\n1. Testing Upwork...")
    upwork = scrape_upwork()
    if upwork:
        print(f"✅ Found {len(upwork)} jobs")
        print(f"Example: {upwork[0]['title']}")
    
    print("\n2. Testing We Work Remotely...")
    wwr = scrape_weworkremotely()
    if wwr:
        print(f"✅ Found {len(wwr)} jobs")
        print(f"Example: {wwr[0]['title']}")
    
    print("\n3. Testing CryptoJobsList...")
    crypto = scrape_cryptojobs()
    if crypto:
        print(f"✅ Found {len(crypto)} jobs")
        print(f"Example: {crypto[0]['title']}")
