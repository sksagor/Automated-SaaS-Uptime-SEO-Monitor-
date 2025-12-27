# apps/monitor/services/scraper.py
import asyncio
import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, List, Optional, Tuple

class WebsiteScraper:
    """Web scraper using requests + BeautifulSoup (no Playwright for now)"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check_uptime(self, url: str) -> Tuple[str, float, Optional[int]]:
        """Check website uptime and response time"""
        start_time = time.time()
        
        try:
            response = self.session.get(
                url, 
                timeout=self.timeout, 
                allow_redirects=True,
                verify=False  # Warning: for testing only!
            )
            response_time = time.time() - start_time
            status_code = response.status_code
            
            if response.status_code == 200:
                if response_time < 2:
                    return 'up', response_time, status_code
                else:
                    return 'slow', response_time, status_code
            else:
                return 'down', response_time, status_code
                
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return 'timeout', response_time, None
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return 'down', response_time, None
    
    def analyze_seo(self, url: str, keywords: List[str] = None) -> Dict:
        """Perform SEO analysis using requests + BeautifulSoup"""
        if keywords is None:
            keywords = []
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code != 200:
                return {'error': f'HTTP {response.status_code}', 'status_code': response.status_code}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic SEO elements
            page_title = soup.title.string if soup.title else ''
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_description = meta_desc.get('content', '') if meta_desc else ''
            
            # Count headings
            h1_count = len(soup.find_all('h1'))
            h2_count = len(soup.find_all('h2'))
            
            # Get main text content
            for script in soup(["script", "style"]):
                script.decompose()
            
            main_text = soup.get_text()
            words = main_text.split()
            word_count = len(words)
            
            # Calculate keyword density
            keyword_density = {}
            text_lower = main_text.lower()
            
            for keyword in keywords:
                keyword_lower = keyword.lower().strip()
                if keyword_lower:
                    count = text_lower.count(keyword_lower)
                    density = (count / max(word_count, 1)) * 100
                    keyword_density[keyword] = {
                        'count': count,
                        'density': round(density, 2)
                    }
            
            # Check for broken links (sample)
            broken_links = 0
            links = soup.find_all('a', href=True)[:5]
            
            for link in links:
                href = link['href']
                if href.startswith('http'):
                    try:
                        resp = self.session.head(href, timeout=5, allow_redirects=True)
                        if resp.status_code >= 400:
                            broken_links += 1
                    except:
                        broken_links += 1
            
            return {
                'page_title': page_title[:500],
                'meta_description': meta_description[:500],
                'word_count': word_count,
                'h1_count': h1_count,
                'h2_count': h2_count,
                'keyword_density': keyword_density,
                'broken_links': broken_links,
                'url': url,
                'status_code': response.status_code
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'page_title': '',
                'meta_description': '',
                'word_count': 0,
                'h1_count': 0,
                'h2_count': 0,
                'keyword_density': {},
                'broken_links': 0,
                'status_code': None
            }