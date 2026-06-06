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
            <section class="col-12 col-lg-2">
                <div class="card dashboard-card p-3 mb-3">
                    <button type="button" class="btn btn-primary w-100 fw-semibold" onclick="openCreateReportModal()">
                        <i class="bi bi-plus-circle-fill me-1"></i>
                        Buat Laporan Baru
                    </button>
                </div>

                <div class="card dashboard-card p-3">
                    <h6 class="status-card-title text-uppercase small mb-3">Status Laporan Anda</h6>

                    <div class="d-flex justify-content-between align-items-center border-bottom py-2 status-item">
                        <span>
                            <i class="bi bi-pencil-square me-1"></i>
                            Draf
                        </span>
                        <span class="badge bg-secondary summary-badge" id="summary-draft">0</span>
                    </div>

                    <div class="d-flex justify-content-between align-items-center border-bottom py-2 status-item">
                        <span>
                            <i class="bi bi-send-fill me-1 text-warning"></i>
                            Diajukan
                        </span>
                        <span class="badge bg-warning summary-badge" id="summary-reported">0</span>
                    </div>

                    <div class="d-flex justify-content-between align-items-center border-bottom py-2 status-item">
                        <span>
                            <i class="bi bi-patch-check-fill me-1 text-info"></i>
                            Diverifikasi
                        </span>
                        <span class="badge bg-info summary-badge" id="summary-verified">0</span>
                    </div>

                    <div class="d-flex justify-content-between align-items-center border-bottom py-2 status-item">
                        <span>
                            <i class="bi bi-gear-fill me-1 text-primary"></i>
                            Diproses
                        </span>
                        <span class="badge bg-primary summary-badge" id="summary-progress">0</span>
                    </div>

                    <div class="d-flex justify-content-between align-items-center py-2 status-item">
                        <span>
                            <i class="bi bi-check-circle-fill me-1 text-success"></i>
                            Selesai
                        </span>
                        <span class="badge bg-success summary-badge" id="summary-resolved">0</span>
                    </div>
                </div>
            </section>

            <section class="col-12 col-lg-10">
                <ul class="nav nav-tabs mb-3">
                    <li class="nav-item">
                        <button type="button" class="nav-link active" id="tab-my-reports" onclick="loadDashboardData('my_reports', 1)">
                            <i class="bi bi-folder-fill me-1"></i>
                            Laporan Saya
                        </button>
                    </li>
                    <li class="nav-item">
                        <button type="button" class="nav-link" id="tab-feed" onclick="loadDashboardData('feed', 1)">
                            <i class="bi bi-globe2 me-1"></i>
                            Feed Kota (Publik)
                        </button>
                    </li>
                </ul>

                <div id="dashboard-alert"></div>

                <div class="row g-3" id="report-list">
                    <div class="col-12">
                        <div class="card dashboard-card p-4 text-center text-muted">
                            Memuat data laporan...
                        </div>
                    </div>
                </div>

                <div class="d-flex justify-content-center mt-4" id="pagination-container"></div>
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
        if (typeof initDashboard === 'function') {
            initDashboard();
        }
    }
}

function updateNavbar() {
    const navMenu = document.getElementById('nav-menu');
    const isLoggedIn = localStorage.getItem('access_token');
    const username = localStorage.getItem('citizen_username') || 'Warga';

    if (!navMenu) {
        return;
    }

    if (isLoggedIn) {
        navMenu.innerHTML = `
            <li class="nav-item">
                <span class="nav-link">
                    <i class="bi bi-person-circle me-1"></i>
                    Halo, ${username}
                </span>
            </li>
            <li class="nav-item">
                <button class="btn btn-light btn-sm ms-lg-2" onclick="logoutCitizen()">
                    <i class="bi bi-box-arrow-right me-1"></i>
                    Keluar
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