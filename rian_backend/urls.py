# rian_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin (Jazzmin styled)
    path("admin/", admin.site.urls),

    # Shop app (frontend + API)
    path("", include("shop.urls")),
]

# Media files (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = "shop.views.handle_404"
handler500 = "shop.views.handle_500"
