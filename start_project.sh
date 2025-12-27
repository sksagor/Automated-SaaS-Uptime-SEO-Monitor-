#!/bin/bash
# Senior Engineer's Automation Script for Django 2026-2030 Portfolio
UptimeSEO=$1

if [ -z "$UptimeSEO" ]; then
    echo "❌ Error: Please provide a project name. Usage: bash start_project.sh my_project"
    exit 1
fi

echo "🚀 Bootstrapping $UptimeSEO..."

# 1. Create Root and Virtual Environment
mkdir $UptimeSEO && cd $UptimeSEO
python3 -m venv venv

# Platform detection for activation
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# 2. Install Core Tech Stack (2026 Standards)
pip install --upgrade pip
pip install django celery redis playwright reportlab django-environ django-celery-beat

# 3. Create Custom Folder Hierarchy
mkdir -p apps/monitor/services core static media docker
touch apps/monitor/services/scraper.py apps/monitor/services/report_gen.py
touch .env docker/docker-compose.yml requirements.txt

# 4. Initialize Django with 'core' as the management folder
# Using '.' prevents nested folders
django-admin startproject core .

# 5. Create the app inside 'apps' folder
python manage.py startapp monitor apps/monitor

echo "✅ Done! Your project is ready at /$UptimeSEO"
echo "👉 RUN: cd $UptimeSEO && source venv/Scripts/activate (or venv\Scripts\activate)"