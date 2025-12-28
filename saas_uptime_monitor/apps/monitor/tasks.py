
from celery import shared_task
from .models import Website, UptimeLog, SEOLog
import requests
import time
from bs4 import BeautifulSoup
import logging        

logger = logging.getLogger(__name__)

def check_uptime(url, timeout=10):
    """Check website uptime and response time"""
    result = {
        'status_code': 0,
        'response_time': 0,
        'is_up': False,
        'error_message': ''
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response_time = time.time() - start_time
        
        result['status_code'] = response.status_code
        result['response_time'] = round(response_time, 2)
        result['is_up'] = 200 <= response.status_code < 400
        
    except requests.exceptions.RequestException as e:
        result['error_message'] = str(e)
    
    return result

def check_seo(url):
    """Check SEO metrics using BeautifulSoup"""
    result = {
        'title': '',
        'meta_description': '',
        'h1_count': 0,
        'word_count': 0,
        'internal_links': 0,
        'external_links': 0
    }
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title
            title_tag = soup.find('title')
            if title_tag:
                result['title'] = title_tag.text.strip()
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                result['meta_description'] = meta_desc['content'].strip()
            
            # Count H1 tags
            result['h1_count'] = len(soup.find_all('h1'))
            
            # Count words in body
            body = soup.find('body')
            if body:
                text = body.get_text()
                words = text.split()
                result['word_count'] = len(words)
    
    except Exception as e:
        logger.error(f"Error checking SEO for {url}: {str(e)}")
    
    return result

@shared_task
def monitor_website(website_id):
    try:
        website = Website.objects.get(id=website_id, is_active=True)
        
        # Check uptime
        uptime_result = check_uptime(website.url)
        
        # Save uptime log
        UptimeLog.objects.create(
            website=website,
            status_code=uptime_result['status_code'],
            response_time=uptime_result['response_time'],
            is_up=uptime_result['is_up'],
            error_message=uptime_result.get('error_message', '')
        )
        
        # Check SEO if website is up
        if uptime_result['is_up']:
            seo_result = check_seo(website.url)
            
            SEOLog.objects.create(
                website=website,
                title=seo_result.get('title'),
                meta_description=seo_result.get('meta_description'),
                h1_count=seo_result.get('h1_count', 0),
                word_count=seo_result.get('word_count', 0),
                internal_links=seo_result.get('internal_links', 0),
                external_links=seo_result.get('external_links', 0)
            )
        
        logger.info(f"Checked {website.name}: {uptime_result['status_code']}")
        return f"Successfully monitored {website.name}"
        
    except Website.DoesNotExist:
        logger.error(f"Website {website_id} not found or inactive")
        return f"Website {website_id} not found"
    except Exception as e:
        logger.error(f"Error monitoring website {website_id}: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def monitor_all_websites():
    active_websites = Website.objects.filter(is_active=True)
    results = []
    for website in active_websites:
        result = monitor_website.delay(website.id)
        results.append(result)
    return f"Started monitoring {len(results)} websites"