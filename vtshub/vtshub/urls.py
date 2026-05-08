"""
URL configuration for vtshub project.
"""

import os
from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Media files (uploaded images)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hubapp.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

