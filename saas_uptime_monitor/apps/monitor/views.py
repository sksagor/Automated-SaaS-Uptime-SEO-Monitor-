from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Website, UptimeLog, SEOLog

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
        # Generate report logic here
        return redirect('dashboard')
    except Website.DoesNotExist:
        return redirect('dashboard')