from django.conf.urls import url

from cms.dashboard.views.base import DashboardHome, ProcessFeedback
from cms.dashboard.views.category_gap_analysis import CategoryGapAnalysisReports, CategoryGapAnalysisReportUpdate, \
    CategoryGapAnalysisReportCreate, CategoryGapAnalysisReportDetail
from cms.dashboard.views.category_tables import CategoryTables, CategoryTableCreate, CategoryTableDetail, \
    CategoryTableUpdate, CategoryTableAttributeUpdate
from cms.dashboard.views.products import Products, ProductDetail

app_name = 'dashboard'

urlpatterns = [
    url(r'^$', DashboardHome.as_view(), name='home'),
    url(r'category-tables/$', CategoryTables.as_view(), name='category-tables'),
    url(r'category-tables/add/$', CategoryTableCreate.as_view(), name='category-table-create'),
    url(r'category-tables/(?P<pk>\d+)/$', CategoryTableDetail.as_view(), name='category-table'),
    url(r'category-tables/(?P<pk>\d+)/update$', CategoryTableUpdate.as_view(), name='category-table-update'),
    url(r'category-tables/(?P<pk>\d+)/specs$', CategoryTableAttributeUpdate.as_view(), name='category-table-specs'),
    url(r'products/$', Products.as_view(), name='products'),
    url(r'products/(?P<pk>\d+)/$', ProductDetail.as_view(), name='product'),
    url(r'feedback/$', ProcessFeedback.as_view(), name='feedback'),
    url(r'category-gap-reports/$', CategoryGapAnalysisReports.as_view(), name='category-gap-reports'),
    url(r'category-gap-reports/add/$', CategoryGapAnalysisReportCreate.as_view(), name='category-gap-report-create'),
    url(r'category-gap-reports/(?P<pk>\d+)$', CategoryGapAnalysisReportDetail.as_view(), name='category-gap-report'),
    url(r'category-gap-reports/(?P<pk>\d+)/update$', CategoryGapAnalysisReportUpdate.as_view(), name='category-gap-report-update'),
]
