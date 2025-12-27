#!/usr/bin/env python
import os
import sys

# Fix 1: Create __init__.py in apps directory
apps_init = os.path.join('apps', '__init__.py')
if not os.path.exists(apps_init):
    with open(apps_init, 'w') as f:
        f.write('# Apps package\n')

# Fix 2: Update manage.py to set Python path correctly
manage_py_content = '''#!/usr/bin/env python
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''

with open('manage.py', 'w') as f:
    f.write(manage_py_content)

# Fix 3: Create minimal working models.py
models_py_content = '''from django.db import models
from django.contrib.auth.models import User

class Website(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    check_interval = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class UptimeLog(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    status_code = models.IntegerField()
    response_time = models.FloatField()
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
    
    class Meta:
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"SEO Check for {self.website.name}"
'''

models_path = os.path.join('apps', 'monitor', 'models.py')
with open(models_path, 'w') as f:
    f.write(models_py_content)

print("✅ Fixed Django configuration issues!")
print("\nNext steps:")
print("1. Run: python manage.py makemigrations")
print("2. Run: python manage.py migrate")
print("3. Run: python manage.py createsuperuser")
print("4. Run: python manage.py runserver")