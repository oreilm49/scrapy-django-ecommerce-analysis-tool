from django.conf.urls import url

from dashboard.views import CategoryTables, CategoryTableDetail, CategoryTableCreate, CategoryTableUpdate

urlpatterns = [
    url('', CategoryTables.as_view(), name='home'),
    url(r'category-tables/$', CategoryTables.as_view(), name='category-tables'),
    url(r'category-tables/add/$', CategoryTableCreate.as_view(), name='category-table-create'),
    url(r'category-table/(?P<pk>\d+)/$', CategoryTableDetail.as_view(), name='category-table'),
    url(r'category-table/(?P<pk>\d+)/update$', CategoryTableUpdate.as_view(), name='category-table-update'),
]
