from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('websites/', views.website_list, name='website_list'),
    path('websites/add/', views.add_website, name='add_website'),
    path('reports/<int:website_id>/', views.generate_report, name='generate_report'),
]