from django.db.models import Count
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from main_app.models import Report, STATUS_CHOICES


class DashboardView(TemplateView):
    template_name = 'dashboard_24782041/dashboard.html'


class DashboardStatsJsonView(View):
    def get(self, request):
        status_labels = dict(STATUS_CHOICES)

        status_counts = Report.objects.values('status').annotate(
            total=Count('id')
        )

        status_count_map = {
            item['status']: item['total']
            for item in status_counts
        }

        status_distribution = [
            {
                'status': status_code,
                'label': status_labels.get(status_code, status_code),
                'total': status_count_map.get(status_code, 0),
            }
            for status_code, label in STATUS_CHOICES
        ]

        category_distribution = list(
            Report.objects.values('category')
            .annotate(total=Count('id'))
            .order_by('category')
        )

        latest_reported = Report.objects.filter(status='REPORTED').order_by('-created_at')[:5]
        latest_resolved = Report.objects.filter(status='RESOLVED').order_by('-created_at')[:5]

        def serialize_report(report):
            return {
                'id': report.id,
                'title': report.title,
                'category': report.category,
                'location': report.location,
                'status': report.status,
                'status_display': report.get_status_display(),
                'created_at': report.created_at.strftime('%d-%m-%Y %H:%M'),
            }

        data = {
            'status_distribution': status_distribution,
            'category_distribution': category_distribution,
            'latest_reported': [serialize_report(report) for report in latest_reported],
            'latest_resolved': [serialize_report(report) for report in latest_resolved],
        }

        return JsonResponse(data)