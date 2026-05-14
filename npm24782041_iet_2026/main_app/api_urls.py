from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import ReportViewSet

router = DefaultRouter()
router.register(r'report', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]