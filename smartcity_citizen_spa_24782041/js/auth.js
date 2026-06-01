function setupLoginForm() {
    const loginForm = document.getElementById('login-form');

    if (!loginForm) {
        return;
    }

    loginForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const usernameInput = document.getElementById('login-username');
        const passwordInput = document.getElementById('login-password');
        const alertBox = document.getElementById('login-alert');

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        alertBox.innerHTML = '';

        if (!username || !password) {
            alertBox.innerHTML = `
                <div class="alert alert-warning">
                    Username dan password wajib diisi.
                </div>
            `;
            return;
        }

        const result = await requestAPI('/api/token/', 'POST', {
            username: username,
            password: password,
        });

        if (result.ok && result.status === 200) {
            localStorage.setItem('access_token', result.data.access);
            localStorage.setItem('refresh_token', result.data.refresh);
            localStorage.setItem('citizen_username', username);

            alertBox.innerHTML = `
                <div class="alert alert-success">
                    Login berhasil. Mengalihkan ke dashboard...
                </div>
            `;

            setTimeout(function () {
                window.location.hash = '#dashboard';
            }, 600);
        } else {
            alertBox.innerHTML = `
                <div class="alert alert-danger">
                    Login gagal. Periksa kembali username dan password.
                </div>
            `;
        }
    });
}

function logoutCitizen() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('citizen_username');

    window.location.hash = '#login';
}