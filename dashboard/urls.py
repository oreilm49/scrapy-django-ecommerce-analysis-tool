from django.conf.urls import url

from dashboard.views.base import DashboardHome
from dashboard.views.category_tables import CategoryTables, CategoryTableDetail, CategoryTableCreate, CategoryTableUpdate
from dashboard.views.products import Products, ProductDetail

app_name = 'dashboard'

urlpatterns = [
    url(r'home/$', DashboardHome.as_view(), name='home'),
    url(r'category-tables/$', CategoryTables.as_view(), name='category-tables'),
    url(r'category-tables/add/$', CategoryTableCreate.as_view(), name='category-table-create'),
    url(r'category-table/(?P<pk>\d+)/$', CategoryTableDetail.as_view(), name='category-table'),
    url(r'category-table/(?P<pk>\d+)/update$', CategoryTableUpdate.as_view(), name='category-table-update'),
    url(r'products/$', Products.as_view(), name='products'),
    url(r'product/(?P<pk>\d+)/$', ProductDetail.as_view(), name='product'),
]
