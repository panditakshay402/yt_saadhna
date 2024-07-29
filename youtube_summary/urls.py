from django.contrib import admin
from django.urls import path, include
from summary.views import process_youtube_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/summary', process_youtube_url),
]
