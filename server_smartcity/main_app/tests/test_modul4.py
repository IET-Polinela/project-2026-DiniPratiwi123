from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from main_app.models import Report

User = get_user_model()


class CRUDAndValidationTests(APITestCase):
    """
    Pengujian CRUD dasar, validasi input wajib, dan keamanan XSS.
    """

    def setUp(self):
        # Arrange: buat warga dan autentikasi
        self.warga = User.objects.create_user(
            username='warga_crud',
            password='TestPass123!',
            is_admin=False,
            is_staff=False,
        )

        self.client.force_authenticate(user=self.warga)

    def test_FT_01_buat_laporan_dengan_data_lengkap(self):
        """
        FT-01:
        Warga membuat laporan baru dengan data lengkap dan valid.
        """

        # Arrange
        url = reverse('report-list')
        payload = {
            'title': 'Jalan Rusak Dekat Gerbang',
            'category': 'Infrastruktur',
            'description': 'Terdapat lubang besar di dekat gerbang utama.',
            'location': 'Gerbang Utama Kampus',
        }

        jumlah_awal = Report.objects.count()

        # Act
        response = self.client.post(url, payload, format='json')

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "POST laporan valid harus menghasilkan HTTP 201 Created."
        )

        self.assertEqual(
            Report.objects.count(),
            jumlah_awal + 1,
            "Jumlah laporan di database harus bertambah satu."
        )

        laporan = Report.objects.get(title='Jalan Rusak Dekat Gerbang')

        self.assertEqual(
            laporan.reporter,
            self.warga,
            "Field reporter harus otomatis terisi dengan user yang login."
        )

        self.assertEqual(
            laporan.status,
            'DRAFT',
            "Laporan baru dari citizen harus otomatis berstatus DRAFT."
        )

        self.assertEqual(
            response.data['title'],
            payload['title'],
            "Judul di respons harus sama dengan payload."
        )

    def test_FT_02_ditolak_jika_judul_kosong(self):
        """
        FT-02:
        Sistem menolak pembuatan laporan jika field title tidak dikirim.
        """

        # Arrange
        url = reverse('report-list')
        payload = {
            'category': 'Infrastruktur',
            'description': 'Deskripsi laporan tetap diisi.',
            'location': 'Gedung A',
        }

        jumlah_awal = Report.objects.count()

        # Act
        response = self.client.post(url, payload, format='json')

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "POST tanpa title harus menghasilkan HTTP 400 Bad Request."
        )

        self.assertIn(
            'title',
            response.data,
            "Respons validasi harus memuat error untuk field title."
        )

        self.assertEqual(
            Report.objects.count(),
            jumlah_awal,
            "Laporan tidak boleh tersimpan jika title kosong."
        )

    def test_FT_03_ditolak_jika_deskripsi_kosong(self):
        """
        FT-03:
        Sistem menolak pembuatan laporan jika field description tidak dikirim.
        """

        # Arrange
        url = reverse('report-list')
        payload = {
            'title': 'Lampu Mati',
            'category': 'Fasilitas Umum',
            'location': 'Gedung B',
        }

        jumlah_awal = Report.objects.count()

        # Act
        response = self.client.post(url, payload, format='json')

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "POST tanpa description harus menghasilkan HTTP 400 Bad Request."
        )

        self.assertIn(
            'description',
            response.data,
            "Respons validasi harus memuat error untuk field description."
        )

        self.assertEqual(
            Report.objects.count(),
            jumlah_awal,
            "Laporan tidak boleh tersimpan jika description kosong."
        )

    def test_FT_04_xss_script_disimpan_sebagai_string_literal(self):
        """
        FT-04:
        Payload XSS pada deskripsi disimpan sebagai string literal,
        bukan dieksekusi sebagai kode.
        """

        # Arrange
        url = reverse('report-list')
        kode_xss = '<script>alert("xss")</script>'

        payload = {
            'title': 'Laporan XSS Test',
            'category': 'Keamanan',
            'description': kode_xss,
            'location': 'Lab Keamanan Siber',
        }

        # Act
        response = self.client.post(url, payload, format='json')

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Data dengan karakter HTML harus tetap diterima oleh API."
        )

        laporan = Report.objects.get(title='Laporan XSS Test')

        self.assertEqual(
            laporan.description,
            kode_xss,
            "Kode XSS harus tersimpan sebagai string literal di database."
        )

        self.assertIn(
            'script',
            laporan.description.lower(),
            "Deskripsi harus tetap berupa teks biasa yang mengandung kata script."
        )