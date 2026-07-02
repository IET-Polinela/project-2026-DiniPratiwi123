from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import ReportForm
from .models import Report


def home_view(request):
    return render(request, 'main_app/welcome.html')


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_admin and not request.user.is_superuser:
            messages.error(request, 'Akses Ditolak')
            return redirect('report_list')

        return super().dispatch(request, *args, **kwargs)


class AdminCannotEditDeleteReportMixin(AdminRequiredMixin):
    """
    Mixin khusus agar konsep sesuai test dosen:
    admin boleh mengelola workflow status, tetapi tidak boleh edit/delete isi laporan.
    """

    forbidden_message = 'Admin tidak diizinkan mengedit atau menghapus laporan.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_admin and not request.user.is_superuser:
            messages.error(request, 'Akses Ditolak')
            return redirect('report_list')

        raise PermissionDenied(self.forbidden_message)

    def get(self, request, *args, **kwargs):
        raise PermissionDenied(self.forbidden_message)

    def post(self, request, *args, **kwargs):
        raise PermissionDenied(self.forbidden_message)

    def delete(self, request, *args, **kwargs):
        raise PermissionDenied(self.forbidden_message)


class ReportListView(ListView):
    model = Report
    template_name = 'main_app/home.html'
    context_object_name = 'reports'


class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'
    context_object_name = 'report'


class ReportCreateView(AdminRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Laporan berhasil ditambahkan.')
        return response


class ReportUpdateView(AdminCannotEditDeleteReportMixin, UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/edit_report.html'
    success_url = reverse_lazy('report_list')


class ReportDeleteView(AdminCannotEditDeleteReportMixin, DeleteView):
    model = Report
    template_name = 'main_app/delete_report.html'
    success_url = reverse_lazy('report_list')
    context_object_name = 'report'


class ReportUpdateStatusView(AdminRequiredMixin, View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')

        allowed_transitions = {
            'REPORTED': 'VERIFIED',
            'VERIFIED': 'IN_PROGRESS',
            'IN_PROGRESS': 'RESOLVED',
        }

        if report.status in allowed_transitions and allowed_transitions[report.status] == new_status:
            report.status = new_status
            report.save()
            messages.success(request, 'Status laporan berhasil diubah.')
        else:
            messages.error(request, 'Perubahan status tidak valid.')

        return redirect('report_list')


def get_status_badge_class(status):
    badge_classes = {
        'REPORTED': 'bg-secondary',
        'VERIFIED': 'bg-info',
        'IN_PROGRESS': 'bg-warning text-dark',
        'RESOLVED': 'bg-success',
    }
    return badge_classes.get(status, 'bg-dark')


def get_next_status(status):
    transitions = {
        'REPORTED': {
            'value': 'VERIFIED',
            'label': 'Verifikasi',
        },
        'VERIFIED': {
            'value': 'IN_PROGRESS',
            'label': 'Proses',
        },
        'IN_PROGRESS': {
            'value': 'RESOLVED',
            'label': 'Selesaikan',
        },
    }
    return transitions.get(status)


class ReportSearchJsonView(View):
    def get(self, request):
        keyword = request.GET.get('q', '').strip()

        reports = Report.objects.all().order_by('-created_at')

        if keyword:
            reports = reports.filter(
                Q(title__icontains=keyword) |
                Q(category__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(location__icontains=keyword) |
                Q(status__icontains=keyword)
            )

        reports = reports[:100]

        data = []

        for report in reports:
            next_status = get_next_status(report.status)

            data.append({
                'id': report.id,
                'title': report.title,
                'category': report.category,
                'description': report.description,
                'location': report.location,
                'status': report.status,
                'status_display': report.get_status_display(),
                'status_class': get_status_badge_class(report.status),
                'created_at': report.created_at.strftime('%d-%m-%Y %H:%M'),
                'detail_url': reverse('report_detail', kwargs={'pk': report.pk}),
                'detail_api_url': reverse('report_detail_api', kwargs={'pk': report.pk}),
                'edit_url': reverse('edit_report', kwargs={'pk': report.pk}),
                'delete_url': reverse('delete_report', kwargs={'pk': report.pk}),
                'update_status_url': reverse('update_status', kwargs={'pk': report.pk}),
                'next_status': next_status,
            })

        return JsonResponse({'reports': data})


class ReportDetailJsonView(View):
    def get(self, request, pk):
        report = get_object_or_404(Report, pk=pk)

        data = {
            'id': report.id,
            'title': report.title,
            'category': report.category,
            'description': report.description,
            'location': report.location,
            'status': report.status,
            'status_display': report.get_status_display(),
            'status_class': get_status_badge_class(report.status),
            'created_at': report.created_at.strftime('%d-%m-%Y %H:%M'),
        }

        return JsonResponse({'report': data})