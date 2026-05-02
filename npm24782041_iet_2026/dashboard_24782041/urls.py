from django.urls import path
from .views import DashboardView, DashboardStatsJsonView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/stats/', DashboardStatsJsonView.as_view(), name='dashboard_stats_api'),
]