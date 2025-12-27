from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Website, UptimeLog, SEOLog
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

@login_required
def dashboard(request):
    websites = Website.objects.filter(owner=request.user)[:5]
    recent_logs = UptimeLog.objects.filter(website__owner=request.user).order_by('-checked_at')[:10]
    
    context = {
        'websites': websites,
        'recent_logs': recent_logs,
    }
    return render(request, 'monitor/dashboard.html', context)

@login_required
def website_list(request):
    websites = Website.objects.filter(owner=request.user)
    return render(request, 'monitor/website_list.html', {'websites': websites})

@login_required
def add_website(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        url = request.POST.get('url')
        
        if name and url:
            Website.objects.create(
                name=name,
                url=url,
                owner=request.user
            )
            return redirect('website_list')
    
    return render(request, 'monitor/add_website.html')

@login_required
def generate_report(request, website_id):
    try:
        website = Website.objects.get(id=website_id, owner=request.user)
        
        # Fetch and analyze the website for SEO data
        try:
            response = requests.get(website.url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract SEO data
            title = soup.title.string.strip() if soup.title else None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_description = meta_desc.get('content') if meta_desc else None
            
            # Count H1 tags
            h1_tags = soup.find_all('h1')
            h1_count = len(h1_tags)
            
            # Count words in body
            body_text = soup.get_text()
            word_count = len(re.findall(r'\w+', body_text))
            
            # Count links
            all_links = soup.find_all('a', href=True)
            internal_links = 0
            external_links = 0
            
            base_domain = urlparse(website.url).netloc
            
            for link in all_links:
                href = link['href']
                parsed_href = urlparse(href)
                if parsed_href.netloc == '' or parsed_href.netloc == base_domain:
                    internal_links += 1
                else:
                    external_links += 1
            
            # Create SEO log entry
            seo_log = SEOLog.objects.create(
                website=website,
                title=title,
                meta_description=meta_description,
                h1_count=h1_count,
                word_count=word_count,
                internal_links=internal_links,
                external_links=external_links
            )
            
            messages.success(request, f"SEO report generated for {website.name}")
            
            # Redirect to the report display page
            return redirect('view_report', website_id=website.id)
            
        except requests.RequestException as e:
            messages.error(request, f"Could not fetch website: {str(e)}")
            return redirect('website_list')
            
    except Website.DoesNotExist:
        messages.error(request, "Website not found or access denied.")
        return redirect('website_list')

@login_required
def toggle_website(request, website_id):
    website = get_object_or_404(Website, id=website_id, owner=request.user)
    
    # Toggle the active status
    website.is_active = not website.is_active
    website.save()
    
    if website.is_active:
        messages.success(request, f"{website.name} has been activated.")
    else:
        messages.success(request, f"{website.name} has been deactivated.")
    
    # Return to website list
    return redirect('website_list')

@login_required
def view_report(request, website_id):
    website = get_object_or_404(Website, id=website_id, owner=request.user)
    
    # Get the latest SEO report for this website
    latest_seo_report = SEOLog.objects.filter(website=website).order_by('-checked_at').first()
    
    # Get all SEO reports for charts
    seo_reports = SEOLog.objects.filter(website=website).order_by('-checked_at')[:10]
    
    # Get uptime data for last 50 checks
    uptime_logs = UptimeLog.objects.filter(website=website).order_by('-checked_at')[:50]
    
    context = {
        'website': website,
        'report': latest_seo_report,
        'seo_reports': seo_reports,
        'uptime_logs': uptime_logs,
    }
    
    return render(request, 'monitor/report.html', context)

# Optional: If you want a delete website function
@login_required
def delete_website(request, website_id):
    website = get_object_or_404(Website, id=website_id, owner=request.user)
    
    if request.method == 'POST':
        website_name = website.name
        website.delete()
        messages.success(request, f"Website '{website_name}' deleted successfully.")
        return redirect('website_list')
    
    # If not POST method, show confirmation page
    return render(request, 'monitor/confirm_delete.html', {'website': website})
