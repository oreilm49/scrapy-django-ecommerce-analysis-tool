from django.contrib import admin
from django.http import HttpResponseServerError
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cms.dashboard.urls', namespace='dashboard')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('accounts/', include('django.contrib.auth.urls')),
]


def my_test_500_view(request):
    return HttpResponseServerError()


urlpatterns += [path('trigger_500/', my_test_500_view)]
