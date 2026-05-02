from django.urls import path
from .views import (
    home_view,
    ReportListView,
    ReportDetailView,
    ReportCreateView,
    ReportUpdateView,
    ReportDeleteView,
    ReportUpdateStatusView,
    ReportSearchJsonView,
    ReportDetailJsonView,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('reports/', ReportListView.as_view(), name='report_list'),
    path('report/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('add/', ReportCreateView.as_view(), name='add_report'),
    path('edit/<int:pk>/', ReportUpdateView.as_view(), name='edit_report'),
    path('delete/<int:pk>/', ReportDeleteView.as_view(), name='delete_report'),
    path('update-status/<int:pk>/', ReportUpdateStatusView.as_view(), name='update_status'),

    path('api/reports/search/', ReportSearchJsonView.as_view(), name='report_search_api'),
    path('api/report/<int:pk>/detail/', ReportDetailJsonView.as_view(), name='report_detail_api'),
]