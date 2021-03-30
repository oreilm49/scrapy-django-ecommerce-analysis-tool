from django.conf.urls import url

from cms.api.views import Contact

app_name = 'api'

urlpatterns = [
    url(r'contact/$', Contact.as_view(), name='contact'),
]
