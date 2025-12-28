from django.db import models
from django.contrib.auth.models import User

class Website(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    check_interval = models.IntegerField(default=5)  # minutes
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class UptimeLog(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    status_code = models.IntegerField()
    response_time = models.FloatField()  # in seconds
    is_up = models.BooleanField(default=True)
    checked_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"{self.website.name} - {'UP' if self.is_up else 'DOWN'}"

class SEOLog(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    h1_count = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)
    internal_links = models.IntegerField(default=0)
    external_links = models.IntegerField(default=0)
    checked_at = models.DateTimeField(auto_now_add=True)
    
    # NEW FIELDS START HERE
    seo_score = models.IntegerField(default=0)
    seo_friendliness = models.IntegerField(default=0)
    content_quality = models.IntegerField(default=0)
    duplicate_percentage = models.FloatField(default=0)
    
    # Header analysis
    h2_count = models.IntegerField(default=0)
    h3_count = models.IntegerField(default=0)
    h4_count = models.IntegerField(default=0)
    h5_count = models.IntegerField(default=0)
    h6_count = models.IntegerField(default=0)
    
    # Image analysis
    images_without_alt = models.IntegerField(default=0)
    total_images = models.IntegerField(default=0)
    
    # Content issues
    has_missing_meta_description = models.BooleanField(default=False)
    has_missing_title = models.BooleanField(default=False)
    has_missing_h1 = models.BooleanField(default=False)
    has_multiple_h1 = models.BooleanField(default=False)
    has_short_content = models.BooleanField(default=False)
    
    # Keyword analysis
    top_keywords = models.TextField(blank=True, null=True)
    keyword_density = models.TextField(blank=True, null=True)
    
    # Technical SEO
    has_viewport_meta = models.BooleanField(default=False)
    has_favicon = models.BooleanField(default=False)
    
    # Google terms analysis
    google_terms_score = models.IntegerField(default=0)
    google_terms_issues = models.TextField(blank=True, null=True)
    # NEW FIELDS END HERE
    
    class Meta:
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"SEO Check for {self.website.name}"
    
    # Property to parse JSON data
    @property
    def parsed_top_keywords(self):
        import json
        try:
            if self.top_keywords:
                return json.loads(self.top_keywords)
        except:
            pass
        return {}
    
    @property
    def parsed_google_terms_issues(self):
        import json
        try:
            if self.google_terms_issues:
                return json.loads(self.google_terms_issues)
        except:
            pass
        return []