from django.contrib import admin
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('cms.dashboard.urls', namespace='dashboard')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('accounts/', include('django.contrib.auth.urls')),
]
