const routes = {
    login: `
        <div class="row justify-content-center">
            <div class="col-12 col-md-8 col-lg-5">
                <div class="card hero-card p-4">
                    <div class="text-center mb-4">
                        <div class="feature-icon mb-3">
                            <i class="bi bi-person-lock"></i>
                        </div>
                        <h3 class="fw-bold">Login Citizen</h3>
                        <p class="text-muted mb-0">
                            Masuk untuk mengakses Portal Citizen Smart City.
                        </p>
                    </div>

                    <div id="login-alert"></div>

                    <form id="login-form">
                        <div class="mb-3">
                            <label for="login-username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="login-username" placeholder="Masukkan username" required>
                        </div>

                        <div class="mb-3">
                            <label for="login-password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="login-password" placeholder="Masukkan password" required>
                        </div>

                        <button type="submit" class="btn btn-primary w-100">
                            <i class="bi bi-box-arrow-in-right me-1"></i>
                            Login
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `,

    dashboard: `
        <div class="row g-4">
            <section class="col-12 col-lg-3">
                <div class="card dashboard-card p-3 h-100">
                    <div class="feature-icon mb-3">
                        <i class="bi bi-person-circle"></i>
                    </div>
                    <h5 class="fw-bold">Profil Citizen</h5>
                    <p class="text-muted mb-2">Selamat datang di Citizen Portal.</p>
                    <p class="mb-0">
                        <strong>User:</strong>
                        <span id="dashboard-username">-</span>
                    </p>
                </div>
            </section>

            <section class="col-12 col-lg-6">
                <div class="card dashboard-card p-3 h-100">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div>
                            <h4 class="fw-bold mb-1">Dashboard Laporan</h4>
                            <p class="text-muted mb-0">
                                Portal ini digunakan untuk mengakses layanan pelaporan warga.
                            </p>
                        </div>
                        <div class="feature-icon">
                            <i class="bi bi-speedometer2"></i>
                        </div>
                    </div>

                    <div class="alert alert-primary mb-0">
                        <i class="bi bi-info-circle me-1"></i>
                        Login berhasil. Token JWT sudah tersimpan di Local Storage.
                    </div>
                </div>
            </section>

            <section class="col-12 col-lg-3">
                <div class="card dashboard-card p-3 h-100">
                    <div class="feature-icon mb-3">
                        <i class="bi bi-shield-lock"></i>
                    </div>
                    <h5 class="fw-bold">Autentikasi</h5>
                    <p class="text-muted">
                        Access token akan digunakan untuk request API berikutnya.
                    </p>
                    <button class="btn btn-outline-danger w-100" onclick="logoutCitizen()">
                        <i class="bi bi-box-arrow-right me-1"></i>
                        Logout
                    </button>
                </div>
            </section>
        </div>
    `,
};

function handleRoute() {
    const hash = window.location.hash.replace('#', '') || 'login';
    const appContent = document.getElementById('app-content');

    if (!appContent) {
        return;
    }

    if (hash === 'dashboard' && !localStorage.getItem('access_token')) {
        window.location.hash = '#login';
        return;
    }

    appContent.innerHTML = routes[hash] || routes.login;

    updateNavbar();

    if (hash === 'login') {
        setupLoginForm();
    }

    if (hash === 'dashboard') {
        const usernameElement = document.getElementById('dashboard-username');
        const username = localStorage.getItem('citizen_username') || 'Citizen';

        if (usernameElement) {
            usernameElement.textContent = username;
        }
    }
}

function updateNavbar() {
    const navMenu = document.getElementById('nav-menu');
    const isLoggedIn = localStorage.getItem('access_token');

    if (!navMenu) {
        return;
    }

    if (isLoggedIn) {
        navMenu.innerHTML = `
            <li class="nav-item">
                <a class="nav-link" href="#dashboard">
                    <i class="bi bi-grid-1x2-fill me-1"></i>
                    Dashboard
                </a>
            </li>
            <li class="nav-item">
                <button class="btn btn-light btn-sm ms-lg-2" onclick="logoutCitizen()">
                    <i class="bi bi-box-arrow-right me-1"></i>
                    Logout
                </button>
            </li>
        `;
    } else {
        navMenu.innerHTML = `
            <li class="nav-item">
                <a class="nav-link" href="#login">
                    <i class="bi bi-box-arrow-in-right me-1"></i>
                    Login
                </a>
            </li>
        `;
    }
}

window.addEventListener('hashchange', handleRoute);
window.addEventListener('load', handleRoute);