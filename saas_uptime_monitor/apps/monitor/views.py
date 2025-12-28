from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Website, UptimeLog, SEOLog
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import json
from collections import Counter

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
            
            # Count other header tags
            h2_count = len(soup.find_all('h2'))
            h3_count = len(soup.find_all('h3'))
            h4_count = len(soup.find_all('h4'))
            h5_count = len(soup.find_all('h5'))
            h6_count = len(soup.find_all('h6'))
            
            # Count words in body and analyze content
            body_text = soup.get_text()
            words = re.findall(r'\w+', body_text.lower())
            word_count = len(words)
            
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
            
            # Image analysis
            all_images = soup.find_all('img')
            total_images = len(all_images)
            images_without_alt = sum(1 for img in all_images if not img.get('alt'))
            
            # Content issues detection
            has_missing_meta_description = meta_description is None or len(meta_description.strip()) == 0
            has_missing_title = title is None or len(title.strip()) == 0
            has_missing_h1 = h1_count == 0
            has_multiple_h1 = h1_count > 1
            has_short_content = word_count < 300
            
            # Keyword analysis (basic)
            top_keywords = {}
            keyword_density = {}
            if words:
                # Remove common stop words
                stop_words = {'the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'but', 'or', 'as', 'if', 'then', 'else', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'}
                
                # Count word frequencies
                word_freq = Counter(words)
                
                # Filter out stop words and short words
                filtered_words = {k: v for k, v in word_freq.items() 
                                 if k not in stop_words and len(k) > 3}
                
                # Get top 10 keywords
                if filtered_words:
                    top_keywords = dict(sorted(filtered_words.items(), 
                                               key=lambda x: x[1], 
                                               reverse=True)[:10])
                    
                    # Calculate keyword density (percentage)
                    keyword_density = {k: round((v / word_count) * 100, 2) 
                                      for k, v in top_keywords.items()}
            
            # Duplicate content estimation (simplified)
            duplicate_percentage = 0.0
            if word_count > 0:
                # Simple check for repeated sentences
                sentences = re.split(r'[.!?]+', body_text)
                unique_sentences = set()
                for sentence in sentences:
                    clean_sentence = sentence.strip().lower()
                    if len(clean_sentence) > 20:  # Only consider meaningful sentences
                        unique_sentences.add(clean_sentence)
                
                if sentences and len(unique_sentences) > 0:
                    duplicate_percentage = round(
                        (1 - len(unique_sentences) / len(sentences)) * 100, 
                        1
                    )
            
            # Mobile/responsive check
            has_viewport_meta = soup.find('meta', attrs={'name': 'viewport'}) is not None
            has_favicon = (soup.find('link', rel='icon') is not None or 
                          soup.find('link', rel='shortcut icon') is not None)
            
            # Calculate SEO scores
            # SEO Friendliness Score (0-100)
            seo_friendliness = 0
            if title and 50 <= len(title) <= 60:
                seo_friendliness += 15
            elif title:
                seo_friendliness += 5
                
            if meta_description and 120 <= len(meta_description) <= 160:
                seo_friendliness += 15
            elif meta_description:
                seo_friendliness += 5
                
            if h1_count == 1:
                seo_friendliness += 20
            elif h1_count > 1:
                seo_friendliness += 5
                
            if h2_count >= 2:
                seo_friendliness += 10
            elif h2_count == 1:
                seo_friendliness += 5
                
            if has_viewport_meta:
                seo_friendliness += 10
                
            if word_count >= 500:
                seo_friendliness += 15
            elif word_count >= 300:
                seo_friendliness += 10
            else:
                seo_friendliness += 5
                
            if images_without_alt == 0:
                seo_friendliness += 10
            elif images_without_alt < 3:
                seo_friendliness += 5
                
            if duplicate_percentage < 10:
                seo_friendliness += 10
            elif duplicate_percentage < 20:
                seo_friendliness += 5
            
            # Content Quality Score (0-100)
            content_quality = 0
            if word_count >= 800:
                content_quality += 25
            elif word_count >= 500:
                content_quality += 20
            elif word_count >= 300:
                content_quality += 15
            else:
                content_quality += 5
                
            if h1_count == 1:
                content_quality += 15
                
            if h2_count >= 2:
                content_quality += 15
            elif h2_count == 1:
                content_quality += 10
                
            if duplicate_percentage < 5:
                content_quality += 20
            elif duplicate_percentage < 15:
                content_quality += 10
            elif duplicate_percentage < 25:
                content_quality += 5
                
            if images_without_alt == 0:
                content_quality += 15
            elif images_without_alt < 3:
                content_quality += 10
            elif images_without_alt < 6:
                content_quality += 5
                
            if top_keywords:
                content_quality += 10
            
            # Google Terms Score (0-100)
            google_terms_score = 100
            google_terms_issues = []
            
            if has_missing_title:
                google_terms_score -= 20
                google_terms_issues.append("Missing page title")
                
            if has_missing_meta_description:
                google_terms_score -= 15
                google_terms_issues.append("Missing meta description")
                
            if has_missing_h1:
                google_terms_score -= 20
                google_terms_issues.append("Missing H1 tag")
                
            if images_without_alt > 0:
                deduction = min(images_without_alt * 3, 25)
                google_terms_score -= deduction
                google_terms_issues.append(f"{images_without_alt} images without alt text")
                
            if word_count < 300:
                google_terms_score -= 20
                google_terms_issues.append("Content too short (less than 300 words)")
                
            if duplicate_percentage > 30:
                google_terms_score -= 15
                google_terms_issues.append(f"High duplicate content ({duplicate_percentage}%)")
                
            if not has_viewport_meta:
                google_terms_score -= 10
                google_terms_issues.append("Missing viewport meta tag (not mobile-friendly)")
            
            # Ensure score is between 0-100
            google_terms_score = max(0, min(100, google_terms_score))
            
            # Overall SEO Score (average of three scores)
            seo_score = round((seo_friendliness + content_quality + google_terms_score) / 3)
            
            # Create SEO log entry with all fields
            seo_log = SEOLog.objects.create(
                website=website,
                title=title,
                meta_description=meta_description,
                h1_count=h1_count,
                word_count=word_count,
                internal_links=internal_links,
                external_links=external_links,
                # New fields
                seo_score=seo_score,
                seo_friendliness=seo_friendliness,
                content_quality=content_quality,
                duplicate_percentage=duplicate_percentage,
                h2_count=h2_count,
                h3_count=h3_count,
                h4_count=h4_count,
                h5_count=h5_count,
                h6_count=h6_count,
                images_without_alt=images_without_alt,
                total_images=total_images,
                has_missing_meta_description=has_missing_meta_description,
                has_missing_title=has_missing_title,
                has_missing_h1=has_missing_h1,
                has_multiple_h1=has_multiple_h1,
                has_short_content=has_short_content,
                top_keywords=json.dumps(top_keywords),
                keyword_density=json.dumps(keyword_density),
                has_viewport_meta=has_viewport_meta,
                has_favicon=has_favicon,
                google_terms_score=google_terms_score,
                google_terms_issues=json.dumps(google_terms_issues)
            )
            
            messages.success(request, f"Comprehensive SEO report generated for {website.name}")
            
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