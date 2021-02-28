from django.conf.urls import url

from dashboard.views import CategoryTables, CategoryTableDetail

urlpatterns = [
    url(r'category-tables/', CategoryTables.as_view(), name='category-tables'),
    url(r'category-table/(?P<pk>\d+)/', CategoryTableDetail.as_view(), name='category-table'),
]
