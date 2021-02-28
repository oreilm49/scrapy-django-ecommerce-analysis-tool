from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from cms import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls'))
]
