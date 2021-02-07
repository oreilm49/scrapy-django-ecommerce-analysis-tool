from django.conf.urls import url

from dashboard.views import CategoryLineUp

urlpatterns = [
    url(r'category/', CategoryLineUp.as_view(), name='category-line-up'),
    url(r'category/(?P<pk>\d+)/', CategoryLineUp.as_view(), name='category-line-up'),
]
