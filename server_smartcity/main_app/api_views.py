from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Report
from .permissions import IsCitizen, IsOwnerDraftOrAdminStatusOnly
from .serializers import ReportSerializer


class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    pagination_class = ReportPagination

    def get_queryset(self):
        user = self.request.user
        tab = self.request.query_params.get('tab')

        queryset = Report.objects.all().order_by('-updated_at')

        if tab == 'my_reports':
            return queryset.filter(reporter=user)

        # Feed Kota menampilkan semua laporan yang sudah diajukan,
        # termasuk laporan milik user login.
        # Laporan DRAFT tetap tidak ditampilkan di Feed Kota.
        if tab == 'feed':
            return queryset.exclude(status='DRAFT')

        if user.is_superuser or getattr(user, 'is_admin', False):
            return queryset.exclude(status='DRAFT')

        return queryset.filter(
            Q(reporter=user) | ~Q(status='DRAFT')
        )

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsCitizen()]

        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerDraftOrAdminStatusOnly()]

        if self.action == 'submit':
            return [permissions.IsAuthenticated(), IsCitizen()]

        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        report = self.get_object()

        if report.reporter != request.user:
            return Response(
                {'detail': 'Anda hanya dapat submit laporan milik sendiri.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if report.status != 'DRAFT':
            return Response(
                {'detail': 'Hanya laporan berstatus DRAFT yang dapat disubmit.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        report.status = 'REPORTED'
        report.save()

        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)