from django.conf.urls import url

from cms.dashboard.views.base import DashboardHome
from cms.dashboard.views.category_tables import CategoryTables, CategoryTableCreate, CategoryTableDetail, \
    CategoryTableUpdate
from cms.dashboard.views.products import Products, ProductDetail

app_name = 'dashboard'

urlpatterns = [
    url(r'home/$', DashboardHome.as_view(), name='home'),
    url(r'category-tables/$', CategoryTables.as_view(), name='category-tables'),
    url(r'category-tables/add/$', CategoryTableCreate.as_view(), name='category-table-create'),
    url(r'category-tables/(?P<pk>\d+)/$', CategoryTableDetail.as_view(), name='category-table'),
    url(r'category-tables/(?P<pk>\d+)/update$', CategoryTableUpdate.as_view(), name='category-table-update'),
    url(r'products/$', Products.as_view(), name='products'),
    url(r'products/(?P<pk>\d+)/$', ProductDetail.as_view(), name='product'),
]
