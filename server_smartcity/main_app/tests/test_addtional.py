from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from main_app.models import Report
from main_app.serializers import ReportSerializer
from main_app.views import get_next_status, get_status_badge_class

User = get_user_model()


# =============================================================================
# ADDITIONAL TESTS FOR STATEMENT COVERAGE
# =============================================================================


class SerializerAndModelCoverageTests(APITestCase):
    """
    Kelas pengujian tambahan untuk menaikkan coverage model dan serializer.

    Fokus:
    - Memastikan __str__ model Report bekerja benar.
    - Memastikan serializer tetap aman ketika tidak memiliki request context.
    - Memastikan serializer menyamarkan reporter pada kondisi publik.
    """

    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga_str_test',
            password='Password123!',
            is_admin=False,
            is_staff=False,
        )

    def test_report_model_str(self):
        """
        Menguji str(report) agar memanggil __str__ dan mengembalikan judul laporan.
        """

        # Arrange
        report = Report.objects.create(
            title='Laporan Str Uji',
            category='Lainnya',
            description='Deskripsi',
            location='Lokasi',
            status='REPORTED',
            reporter=self.warga,
        )

        # Act
        result = str(report)

        # Assert
        self.assertEqual(result, 'Laporan Str Uji')

    def test_report_serializer_no_request_context(self):
        """
        Menguji serializer tanpa menyertakan request dalam context.
        """

        # Arrange
        report = Report.objects.create(
            title='Laporan Serializer Uji',
            category='Lainnya',
            description='Deskripsi',
            location='Lokasi',
            status='REPORTED',
            reporter=self.warga,
        )

        # Act
        serializer = ReportSerializer(report, context={})
        data = serializer.data

        # Assert
        self.assertFalse(data['is_owner'])
        self.assertEqual(data['reporter'], 'Warga Anonim')


class MainAppMonolithicViewsCoverageTests(TestCase):
    """
    Menguji view monolitik di main_app/views.py untuk mencakup alur GET, POST,
    validasi akses, JSON API non-DRF, update status, dan helper function.

    Konsep mengikuti contoh dosen:
    - Admin boleh create laporan.
    - Admin boleh update status laporan.
    - Admin tidak boleh edit/delete isi laporan.
    """

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_mono',
            password='Password123!',
            is_admin=True,
            is_staff=True,
        )

        self.citizen = User.objects.create_user(
            username='citizen_mono',
            password='Password123!',
            is_admin=False,
            is_staff=False,
        )

        self.report = Report.objects.create(
            title='Laporan Monolitik Uji',
            category='Infrastruktur',
            description='Ada kerusakan infrastruktur.',
            location='Bandung',
            status='REPORTED',
            reporter=self.citizen,
        )

    # -------------------------------------------------------------------------
    # Helper Function Coverage
    # -------------------------------------------------------------------------

    def test_get_status_badge_class_known_status(self):
        """
        Menguji helper get_status_badge_class untuk status valid.
        """

        # Act
        result = get_status_badge_class('REPORTED')

        # Assert
        self.assertEqual(result, 'bg-secondary')

    def test_get_status_badge_class_unknown_status(self):
        """
        Menguji helper get_status_badge_class untuk status tidak dikenal.
        """

        # Act
        result = get_status_badge_class('UNKNOWN')

        # Assert
        self.assertEqual(result, 'bg-dark')

    def test_get_next_status_valid(self):
        """
        Menguji helper get_next_status untuk transisi valid.
        """

        # Act
        result = get_next_status('REPORTED')

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'VERIFIED')
        self.assertEqual(result['label'], 'Verifikasi')

    def test_get_next_status_final_or_unknown(self):
        """
        Menguji helper get_next_status untuk status final/tidak memiliki transisi.
        """

        # Act
        result = get_next_status('RESOLVED')

        # Assert
        self.assertIsNone(result)

    # -------------------------------------------------------------------------
    # JSON API Non-DRF Coverage
    # -------------------------------------------------------------------------

    def test_report_detail_api_valid(self):
        """
        Menguji endpoint JSON detail laporan yang valid.
        """

        # Arrange
        url = reverse('report_detail_api', kwargs={'pk': self.report.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn('report', data)
        self.assertEqual(data['report']['title'], 'Laporan Monolitik Uji')

    def test_report_detail_api_invalid(self):
        """
        Menguji endpoint JSON detail laporan dengan ID tidak valid.
        """

        # Arrange
        url = reverse('report_detail_api', kwargs={'pk': 99999})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_report_search_unauthenticated(self):
        """
        Menguji live search JSON tanpa login.
        Nama route disesuaikan dengan project: report_search_api.
        """

        # Arrange
        url = reverse('report_search_api') + '?q=Monolitik'

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn('reports', data)
        self.assertGreaterEqual(len(data['reports']), 1)

    def test_report_search_citizen(self):
        """
        Menguji live search JSON sebagai citizen.
        """

        # Arrange
        self.client.login(username='citizen_mono', password='Password123!')
        url = reverse('report_search_api') + '?q=Monolitik'

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn('reports', data)

    def test_report_search_admin(self):
        """
        Menguji live search JSON sebagai admin.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('report_search_api') + '?q=Monolitik'

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn('reports', data)
        self.assertGreaterEqual(len(data['reports']), 1)

    # -------------------------------------------------------------------------
    # Home & Report List View Coverage
    # -------------------------------------------------------------------------

    def test_home_view(self):
        """
        Menguji halaman home utama.
        """

        # Arrange
        url = reverse('home')

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'main_app/welcome.html')

    def test_report_list_view_unauthenticated(self):
        """
        Menguji halaman daftar laporan tanpa login.
        Template disesuaikan dengan project: main_app/home.html.
        """

        # Arrange
        url = reverse('report_list')

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'main_app/home.html')

    def test_report_list_view_citizen(self):
        """
        Menguji halaman daftar laporan sebagai citizen.
        """

        # Arrange
        self.client.login(username='citizen_mono', password='Password123!')
        url = reverse('report_list')

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'main_app/home.html')

    def test_report_list_view_admin(self):
        """
        Menguji halaman daftar laporan sebagai admin.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('report_list')

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'main_app/home.html')

    # -------------------------------------------------------------------------
    # Create View Coverage
    # -------------------------------------------------------------------------

    def test_report_create_view_unauthenticated(self):
        """
        Menguji halaman tambah laporan tanpa login.
        """

        # Arrange
        url = reverse('add_report')

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_report_create_view_citizen(self):
        """
        Menguji citizen tidak boleh membuka halaman tambah laporan admin.
        """

        # Arrange
        self.client.login(username='citizen_mono', password='Password123!')
        url = reverse('add_report')

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('report_list'))

    def test_report_create_view_admin_get(self):
        """
        Menguji admin dapat membuka halaman tambah laporan.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('add_report')

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'main_app/add_report.html')

    def test_report_create_view_admin_post_valid(self):
        """
        Menguji admin dapat menambah laporan melalui form monolitik.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('add_report')

        payload = {
            'title': 'Laporan Form Baru',
            'category': 'Infrastruktur',
            'description': 'Deskripsi baru.',
            'location': 'Jakarta',
            'status': 'DRAFT',
        }

        # Act
        response = self.client.post(url, payload)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('report_list'))
        self.assertTrue(Report.objects.filter(title='Laporan Form Baru').exists())

    # -------------------------------------------------------------------------
    # Detail View Coverage
    # -------------------------------------------------------------------------

    def test_report_detail_view_unauthenticated(self):
        """
        Menguji halaman detail laporan tanpa login.
        """

        # Arrange
        url = reverse('report_detail', kwargs={'pk': self.report.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_report_detail_view_citizen(self):
        """
        Menguji halaman detail laporan sebagai citizen.
        """

        # Arrange
        self.client.login(username='citizen_mono', password='Password123!')
        url = reverse('report_detail', kwargs={'pk': self.report.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_report_detail_view_admin(self):
        """
        Menguji halaman detail laporan sebagai admin.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('report_detail', kwargs={'pk': self.report.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -------------------------------------------------------------------------
    # Update View Coverage
    # -------------------------------------------------------------------------

    def test_report_update_view_unauthenticated(self):
        """
        Menguji halaman edit laporan tanpa login.
        """

        # Arrange
        url = reverse('edit_report', kwargs={'pk': self.report.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_report_update_view_citizen(self):
        """
        Menguji citizen tidak boleh membuka halaman edit laporan admin.
        """

        # Arrange
        self.client.login(username='citizen_mono', password='Password123!')
        url = reverse('edit_report', kwargs={'pk': self.report.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('report_list'))

    def test_report_update_view_admin_get(self):
        """
        Menguji admin tidak boleh membuka halaman edit laporan.
        Sesuai konsep dosen, output yang diharapkan adalah 403.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('edit_report', kwargs={'pk': self.report.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_report_update_view_admin_post_valid(self):
        """
        Menguji admin tidak boleh mengubah isi laporan melalui form monolitik.
        Data asli harus tetap aman.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('edit_report', kwargs={'pk': self.report.id})

        original_title = self.report.title

        payload = {
            'title': 'Laporan Terupdate Oleh Admin',
            'category': 'Infrastruktur',
            'description': 'Deskripsi terupdate.',
            'location': 'Jakarta',
            'status': 'REPORTED',
        }

        # Act
        response = self.client.post(url, payload)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.report.refresh_from_db()

        self.assertEqual(self.report.title, original_title)
        self.assertNotEqual(self.report.title, 'Laporan Terupdate Oleh Admin')

    # -------------------------------------------------------------------------
    # Delete View Coverage
    # -------------------------------------------------------------------------

    def test_report_delete_view_unauthenticated(self):
        """
        Menguji halaman hapus laporan tanpa login.
        """

        # Arrange
        url = reverse('delete_report', kwargs={'pk': self.report.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_report_delete_view_citizen(self):
        """
        Menguji citizen tidak boleh membuka halaman hapus laporan admin.
        """

        # Arrange
        self.client.login(username='citizen_mono', password='Password123!')
        url = reverse('delete_report', kwargs={'pk': self.report.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('report_list'))

    def test_report_delete_view_admin_get(self):
        """
        Menguji admin tidak boleh membuka halaman hapus laporan.
        Sesuai konsep dosen, output yang diharapkan adalah 403.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('delete_report', kwargs={'pk': self.report.id})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_report_delete_view_admin_post(self):
        """
        Menguji admin tidak boleh menghapus laporan.
        Record laporan harus tetap ada di database.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('delete_report', kwargs={'pk': self.report.id})

        # Act
        response = self.client.post(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Report.objects.filter(id=self.report.id).exists())

    def test_report_delete_view_direct_delete_method(self):
        """
        Menguji pemanggilan langsung method delete tetap ditolak.
        """

        # Arrange
        from main_app.views import ReportDeleteView
        from django.test import RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage

        factory = RequestFactory()
        request = factory.post(reverse('delete_report', kwargs={'pk': self.report.id}))
        request.user = self.admin

        setattr(request, 'session', {})
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)

        view = ReportDeleteView()
        view.setup(request, pk=self.report.id)

        # Act & Assert
        with self.assertRaises(PermissionDenied):
            view.delete(request)

        self.assertTrue(Report.objects.filter(id=self.report.id).exists())

    # -------------------------------------------------------------------------
    # Update Status View Coverage
    # -------------------------------------------------------------------------

    def test_report_update_status_view_unauthenticated(self):
        """
        Menguji update status tanpa login.
        """

        # Arrange
        url = reverse('update_status', kwargs={'pk': self.report.id})

        # Act
        response = self.client.post(url, {'status': 'VERIFIED'})

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_report_update_status_view_citizen(self):
        """
        Menguji citizen tidak boleh update status melalui portal admin.
        """

        # Arrange
        self.client.login(username='citizen_mono', password='Password123!')
        url = reverse('update_status', kwargs={'pk': self.report.id})

        # Act
        response = self.client.post(url, {'status': 'VERIFIED'})

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('report_list'))

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'REPORTED')

    def test_report_update_status_view_admin_valid_transition(self):
        """
        Menguji admin dapat melakukan transisi status valid REPORTED -> VERIFIED.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('update_status', kwargs={'pk': self.report.id})

        # Act
        response = self.client.post(url, {'status': 'VERIFIED'})

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('report_list'))

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'VERIFIED')

    def test_report_update_status_view_admin_invalid_transition(self):
        """
        Menguji admin tidak bisa melompat langsung dari REPORTED ke RESOLVED.
        """

        # Arrange
        self.client.login(username='admin_mono', password='Password123!')
        url = reverse('update_status', kwargs={'pk': self.report.id})

        # Act
        response = self.client.post(url, {'status': 'RESOLVED'})

        # Assert
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('report_list'))

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'REPORTED')