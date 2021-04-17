import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cms.dashboard.urls', namespace='dashboard')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('api/v1/', include('cms.api.urls', namespace='api')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html')),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset_form.html')),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html')),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html')),
    path('accounts/reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_change_done.html')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def trigger_500(request):
    return 1 / 0


urlpatterns += [path('trigger_500/', trigger_500)]
