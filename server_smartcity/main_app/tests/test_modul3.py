from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from main_app.models import Report
from main_app.views import get_next_status

User = get_user_model()


class WorkflowStateTests(APITestCase):
    """
    Pengujian alur kerja status laporan melalui REST API.
    """

    def setUp(self):
        # Arrange: buat warga
        self.warga = User.objects.create_user(
            username='warga_wf',
            password='TestPass123!',
            is_admin=False,
            is_staff=False,
        )

        # Arrange: laporan DRAFT milik warga
        self.laporan_draft = Report.objects.create(
            title='Lampu Kampus Mati',
            category='Fasilitas Umum',
            description='Lampu di depan gedung rektorat tidak menyala.',
            location='Gedung Rektorat',
            status='DRAFT',
            reporter=self.warga,
        )

        # Arrange: laporan REPORTED milik warga
        self.laporan_reported = Report.objects.create(
            title='Saluran Air Tersumbat',
            category='Infrastruktur',
            description='Saluran air di samping kantin tersumbat.',
            location='Kantin Polinela',
            status='REPORTED',
            reporter=self.warga,
        )

        # Arrange: laporan RESOLVED milik warga
        self.laporan_resolved = Report.objects.create(
            title='AC Rusak di Lab',
            category='Fasilitas Umum',
            description='AC di Lab CPS 1 sudah diperbaiki.',
            location='Lab CPS 1',
            status='RESOLVED',
            reporter=self.warga,
        )

    def test_WF_01_warga_mengajukan_draf_menjadi_reported(self):
        """
        WF-01:
        Warga mengajukan laporan dari DRAFT menjadi REPORTED melalui endpoint submit.
        """

        # Arrange
        self.client.force_authenticate(user=self.warga)
        url = reverse('report-submit', kwargs={'pk': self.laporan_draft.pk})

        # Act
        response = self.client.post(url, {}, format='json')

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Submit draf milik sendiri harus berhasil dengan HTTP 200."
        )

        self.laporan_draft.refresh_from_db()

        self.assertEqual(
            self.laporan_draft.status,
            'REPORTED',
            "Status laporan harus berubah dari DRAFT menjadi REPORTED."
        )

    def test_WF_02_tidak_bisa_edit_laporan_yang_sudah_reported(self):
        """
        WF-02:
        Warga tidak boleh mengubah konten laporan yang sudah berstatus REPORTED.
        """

        # Arrange
        self.client.force_authenticate(user=self.warga)
        url = reverse('report-detail', kwargs={'pk': self.laporan_reported.pk})

        judul_awal = self.laporan_reported.title
        deskripsi_awal = self.laporan_reported.description

        payload = {
            'title': 'Judul Diubah Setelah Reported',
            'category': self.laporan_reported.category,
            'description': 'Deskripsi diubah setelah laporan diajukan.',
            'location': self.laporan_reported.location,
            'status': self.laporan_reported.status,
        }

        # Act
        response = self.client.put(url, payload, format='json')

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Laporan REPORTED tidak boleh diedit oleh warga."
        )

        self.laporan_reported.refresh_from_db()

        self.assertEqual(
            self.laporan_reported.title,
            judul_awal,
            "Judul laporan REPORTED tidak boleh berubah."
        )

        self.assertEqual(
            self.laporan_reported.description,
            deskripsi_awal,
            "Deskripsi laporan REPORTED tidak boleh berubah."
        )

    def test_WF_05_laporan_resolved_tidak_bisa_diubah(self):
        """
        WF-05:
        Laporan RESOLVED bersifat final/read-only dan tidak boleh diubah warga.
        """

        # Arrange
        self.client.force_authenticate(user=self.warga)
        url = reverse('report-detail', kwargs={'pk': self.laporan_resolved.pk})

        judul_awal = self.laporan_resolved.title

        payload = {
            'title': 'Judul Diubah Setelah Resolved',
            'category': self.laporan_resolved.category,
            'description': 'Deskripsi diubah setelah resolved.',
            'location': self.laporan_resolved.location,
            'status': self.laporan_resolved.status,
        }

        # Act
        response = self.client.put(url, payload, format='json')

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Laporan RESOLVED tidak boleh diubah oleh warga."
        )

        self.laporan_resolved.refresh_from_db()

        self.assertEqual(
            self.laporan_resolved.title,
            judul_awal,
            "Data laporan RESOLVED harus tetap aman dan tidak berubah."
        )


class AdminWorkflowTests(TestCase):
    """
    Pengujian workflow status laporan melalui portal admin monolitik.
    """

    def setUp(self):
        # Arrange: buat admin
        self.admin = User.objects.create_user(
            username='admin_portal',
            password='AdminPass123!',
            is_admin=True,
            is_staff=True,
        )

        # Arrange: buat warga sebagai reporter
        self.warga = User.objects.create_user(
            username='warga_admin_wf',
            password='TestPass123!',
            is_admin=False,
            is_staff=False,
        )

        # Arrange: laporan REPORTED yang siap diverifikasi admin
        self.laporan_reported = Report.objects.create(
            title='Jalan Rusak di Blok C',
            category='Infrastruktur',
            description='Jalan berlubang parah di area parkir Blok C.',
            location='Blok C Polinela',
            status='REPORTED',
            reporter=self.warga,
        )

    def test_WF_03_admin_mengubah_status_reported_ke_verified(self):
        """
        WF-03:
        Admin mengubah status laporan dari REPORTED menjadi VERIFIED.
        """

        # Arrange
        login_berhasil = self.client.login(
            username='admin_portal',
            password='AdminPass123!'
        )

        self.assertTrue(
            login_berhasil,
            "Admin harus berhasil login sebelum mengubah status laporan."
        )

        url = reverse('update_status', kwargs={'pk': self.laporan_reported.pk})

        # Act
        response = self.client.post(url, {'status': 'VERIFIED'})

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_302_FOUND,
            "Update status admin harus menghasilkan redirect HTTP 302."
        )

        self.assertEqual(
            response.url,
            reverse('report_list'),
            "Setelah update status, admin diarahkan ke daftar laporan."
        )

        self.laporan_reported.refresh_from_db()

        self.assertEqual(
            self.laporan_reported.status,
            'VERIFIED',
            "Status laporan harus berubah dari REPORTED menjadi VERIFIED."
        )

    def test_WF_04_tidak_ada_transisi_langsung_ke_resolved_dari_reported(self):
        """
        WF-04:
        Laporan REPORTED tidak boleh langsung lompat ke RESOLVED.
        Transisi valid berikutnya hanya VERIFIED.
        """

        # Arrange
        login_berhasil = self.client.login(
            username='admin_portal',
            password='AdminPass123!'
        )

        self.assertTrue(
            login_berhasil,
            "Admin harus berhasil login sebelum menguji transisi status."
        )

        next_status = get_next_status('REPORTED')

        # Assert awal: transisi lokal dari REPORTED hanya ke VERIFIED
        self.assertIsNotNone(
            next_status,
            "Status REPORTED harus memiliki transisi berikutnya."
        )

        self.assertEqual(
            next_status['value'],
            'VERIFIED',
            "Transisi valid dari REPORTED harus menuju VERIFIED."
        )

        self.assertNotEqual(
            next_status['value'],
            'RESOLVED',
            "Status REPORTED tidak boleh langsung menuju RESOLVED."
        )

        url = reverse('update_status', kwargs={'pk': self.laporan_reported.pk})

        # Act: admin mencoba lompat langsung ke RESOLVED
        response = self.client.post(url, {'status': 'RESOLVED'})

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_302_FOUND,
            "Transisi invalid tetap mengembalikan redirect ke daftar laporan."
        )

        self.laporan_reported.refresh_from_db()

        self.assertEqual(
            self.laporan_reported.status,
            'REPORTED',
            "Status harus tetap REPORTED karena lompat langsung ke RESOLVED tidak valid."
        )