from django.contrib import admin
from django.urls import path, include
from django.conf import settings          # 1. Import settings
from django.conf.urls.static import static  # 2. Import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("notes.urls")),
]

# 3. Add this line to serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)