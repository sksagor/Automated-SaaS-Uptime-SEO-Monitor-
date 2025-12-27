from django.contrib import admin
from .models import Website, UptimeLog, SEOLog

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'check_interval', 'is_active', 'owner', 'created_at')
    list_filter = ('is_active', 'owner')
    search_fields = ('name', 'url')

@admin.register(UptimeLog)
class UptimeLogAdmin(admin.ModelAdmin):
    list_display = ('website', 'status_code', 'response_time', 'is_up', 'checked_at')
    list_filter = ('is_up', 'website')
    readonly_fields = ('checked_at',)

@admin.register(SEOLog)
class SEOLogAdmin(admin.ModelAdmin):
    list_display = ('website', 'title', 'h1_count', 'word_count', 'checked_at')
    list_filter = ('website',)
    readonly_fields = ('checked_at',)