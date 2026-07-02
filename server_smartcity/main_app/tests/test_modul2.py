from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from main_app.models import Report

User = get_user_model()


class PrivacyAndDataHidingTests(APITestCase):
    """
    Pengujian visibilitas data dan privasi pelapor.
    """

    def setUp(self):
        # Arrange: buat dua warga berbeda
        self.warga_a = User.objects.create_user(
            username='warga_a',
            password='TestPass123!',
            is_admin=False,
            is_staff=False,
        )

        self.warga_b = User.objects.create_user(
            username='warga_b',
            password='TestPass123!',
            is_admin=False,
            is_staff=False,
        )

        # Arrange: draf milik warga B
        self.draft_milik_b = Report.objects.create(
            title='Draf Rahasia Warga B',
            category='Infrastruktur',
            description='Ini adalah draf yang belum diajukan.',
            location='Lokasi Rahasia',
            status='DRAFT',
            reporter=self.warga_b,
        )

        # Arrange: laporan publik milik warga A
        self.laporan_publik_a = Report.objects.create(
            title='Jalan Berlubang di Depan Kampus',
            category='Infrastruktur',
            description='Ada lubang besar yang membahayakan pengendara.',
            location='Jl. Soekarno Hatta',
            status='REPORTED',
            reporter=self.warga_a,
        )

        # Arrange: laporan publik milik warga B
        self.laporan_publik_b = Report.objects.create(
            title='Sampah Menumpuk di Trotoar',
            category='Kebersihan',
            description='Sampah tidak diangkut selama seminggu.',
            location='Jl. Gatot Subroto',
            status='REPORTED',
            reporter=self.warga_b,
        )

    def test_PRIV_01_feed_kota_menyembunyikan_identitas_reporter(self):
        """
        PRIV-01:
        Feed Kota harus menyamarkan identitas semua pelapor menjadi
        'Warga Anonim'.
        """

        # Arrange
        self.client.force_authenticate(user=self.warga_a)
        url = reverse('report-list')

        # Act
        response = self.client.get(url, {'tab': 'feed'})

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Feed Kota harus dapat diakses oleh warga yang sudah login."
        )

        results = response.data.get('results', [])

        self.assertGreater(
            len(results),
            0,
            "Feed Kota harus memiliki minimal satu laporan publik."
        )

        result_ids = [report['id'] for report in results]

        self.assertIn(
            self.laporan_publik_a.id,
            result_ids,
            "Laporan REPORTED milik warga A harus muncul di feed."
        )

        self.assertIn(
            self.laporan_publik_b.id,
            result_ids,
            "Laporan REPORTED milik warga B harus muncul di feed."
        )

        self.assertNotIn(
            self.draft_milik_b.id,
            result_ids,
            "Laporan DRAFT tidak boleh muncul di feed publik."
        )

        for report in results:
            self.assertEqual(
                report['reporter'],
                'Warga Anonim',
                "Identitas pelapor di Feed Kota harus disamarkan."
            )

    def test_PRIV_02_laporan_saya_menampilkan_nama_asli(self):
        """
        PRIV-02:
        Pada tab Laporan Saya, warga harus dapat melihat nama dirinya sendiri
        sebagai pelapor.
        """

        # Arrange
        self.client.force_authenticate(user=self.warga_a)
        url = reverse('report-list')

        # Act
        response = self.client.get(url, {'tab': 'my_reports'})

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Tab my_reports harus dapat diakses oleh warga yang login."
        )

        results = response.data.get('results', [])

        self.assertGreater(
            len(results),
            0,
            "Warga A harus memiliki minimal satu laporan miliknya sendiri."
        )

        for report in results:
            self.assertEqual(
                report['reporter'],
                'warga_a',
                "Pada tab my_reports, reporter harus menampilkan username asli pemilik."
            )

            self.assertTrue(
                report['is_owner'],
                "Pada tab my_reports, laporan milik sendiri harus memiliki is_owner=True."
            )

    def test_PRIV_03_tidak_bisa_baca_draf_orang_lain(self):
        """
        PRIV-03:
        Warga A tidak boleh membaca detail laporan DRAFT milik Warga B.
        Sistem harus menyembunyikan eksistensi data dengan HTTP 404.
        """

        # Arrange
        self.client.force_authenticate(user=self.warga_a)
        url = reverse('report-detail', kwargs={'pk': self.draft_milik_b.pk})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Draf milik warga lain harus disembunyikan dengan HTTP 404."
        )

    def test_PRIV_04_tidak_bisa_modifikasi_draf_orang_lain(self):
        """
        PRIV-04:
        Warga A tidak boleh memodifikasi laporan DRAFT milik Warga B.
        Data asli di database harus tetap aman.
        """

        # Arrange
        self.client.force_authenticate(user=self.warga_a)
        url = reverse('report-detail', kwargs={'pk': self.draft_milik_b.pk})

        judul_awal = self.draft_milik_b.title
        deskripsi_awal = self.draft_milik_b.description

        payload = {
            'title': 'Judul Diubah Paksa',
            'category': self.draft_milik_b.category,
            'description': 'Deskripsi diubah paksa oleh warga lain.',
            'location': self.draft_milik_b.location,
            'status': self.draft_milik_b.status,
        }

        # Act
        response = self.client.put(url, payload, format='json')

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Modifikasi draf milik warga lain harus ditolak dengan HTTP 404."
        )

        self.draft_milik_b.refresh_from_db()

        self.assertEqual(
            self.draft_milik_b.title,
            judul_awal,
            "Judul draf asli tidak boleh berubah."
        )

        self.assertEqual(
            self.draft_milik_b.description,
            deskripsi_awal,
            "Deskripsi draf asli tidak boleh berubah."
        )