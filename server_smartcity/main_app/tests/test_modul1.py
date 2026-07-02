from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthenticationTests(APITestCase):
    """
    Pengujian autentikasi JWT dan pembatasan akses dashboard admin.
    """

    def setUp(self):
        # Arrange: membuat warga biasa
        self.warga = User.objects.create_user(
            username='warga_test',
            password='Password123!',
            is_admin=False,
            is_staff=False,
        )

        # Arrange: membuat admin
        self.admin = User.objects.create_user(
            username='admin_test',
            password='AdminPass123!',
            is_admin=True,
            is_staff=True,
        )

    def test_AUTH_01_login_warga_dengan_kredensial_valid(self):
        """
        AUTH-01:
        Warga login menggunakan username dan password yang valid.
        """

        # Arrange
        url = reverse('token_obtain_pair')
        payload = {
            'username': 'warga_test',
            'password': 'Password123!',
        }

        # Act
        response = self.client.post(url, payload, format='json')

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Login dengan kredensial valid harus menghasilkan HTTP 200."
        )

        self.assertIn(
            'access',
            response.data,
            "Respons login harus memiliki JWT access token."
        )

        self.assertIn(
            'refresh',
            response.data,
            "Respons login harus memiliki JWT refresh token."
        )

    def test_AUTH_02_login_warga_dengan_password_salah(self):
        """
        AUTH-02:
        Login ditolak bila password salah.
        """

        # Arrange
        url = reverse('token_obtain_pair')
        payload = {
            'username': 'warga_test',
            'password': 'passwordSALAH',
        }

        # Act
        response = self.client.post(url, payload, format='json')

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Login dengan password salah harus menghasilkan HTTP 401."
        )

        self.assertNotIn(
            'access',
            response.data,
            "Sistem tidak boleh menerbitkan access token untuk password salah."
        )

    def test_AUTH_03_warga_tidak_bisa_akses_halaman_admin(self):
        """
        AUTH-03:
        Warga biasa yang sudah login tidak boleh membuka dashboard admin.
        Sistem harus mengarahkan warga ke halaman daftar laporan dengan HTTP 302.
        """

        # Arrange: login menggunakan session Django sebagai warga biasa
        login_berhasil = self.client.login(
            username='warga_test',
            password='Password123!'
        )

        self.assertTrue(
            login_berhasil,
            "Warga biasa harus berhasil login sebelum menguji pembatasan dashboard."
        )

        # Act: warga mengakses dashboard admin
        response = self.client.get(reverse('dashboard'))

        # Assert: warga mendapat redirect HTTP 302
        self.assertEqual(
            response.status_code,
            status.HTTP_302_FOUND,
            "Warga biasa harus mendapat HTTP 302 saat mengakses dashboard admin."
        )

        # Assert tambahan: arah redirect menuju daftar laporan
        self.assertEqual(
            response.url,
            reverse('report_list'),
            "Warga biasa harus diarahkan ke halaman daftar laporan."
        )