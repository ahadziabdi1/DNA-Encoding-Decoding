from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='DNK-home'),
    path('download_file/', views.download_file, name='download_file')
]