from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('websites/', views.website_list, name='website_list'),
    path('websites/add/', views.add_website, name='add_website'),
    path('websites/toggle/<int:website_id>/', views.toggle_website, name='toggle_website'),
    path('reports/generate/<int:website_id>/', views.generate_report, name='generate_report'),
    path('reports/view/<int:website_id>/', views.view_report, name='view_report'),
    # Optional delete route:
    # path('websites/delete/<int:website_id>/', views.delete_website, name='delete_website'),
]