const routes = {
    login: `
        <style>
            body {
                background:
                    radial-gradient(circle at 12% 10%, rgba(255, 224, 150, 0.24), transparent 30%),
                    radial-gradient(circle at 88% 16%, rgba(255, 188, 210, 0.22), transparent 32%),
                    linear-gradient(135deg, #fffaf2 0%, #fff6f9 48%, #fffdf2 100%);
            }

            .final-login-page {
                min-height: calc(100vh - 92px);
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 46px 18px;
                color: #3f3037;
            }

            .final-login-card {
                width: 100%;
                max-width: 1040px;
                display: grid;
                grid-template-columns: 1fr 0.95fr;
                overflow: hidden;
                border-radius: 32px;
                background: rgba(255, 255, 255, 0.94);
                border: 1px solid rgba(236, 185, 202, 0.48);
                box-shadow: 0 26px 70px rgba(150, 95, 118, 0.14);
            }

            .final-login-left {
                position: relative;
                overflow: hidden;
                padding: 56px;
                background:
                    radial-gradient(circle at 20% 12%, rgba(255, 224, 150, 0.52), transparent 34%),
                    radial-gradient(circle at 92% 86%, rgba(255, 190, 213, 0.38), transparent 34%),
                    linear-gradient(145deg, #fff8e8 0%, #fff1f6 55%, #fffdf9 100%);
            }

            .final-login-badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 16px;
                margin-bottom: 26px;
                border-radius: 999px;
                color: #c85c82;
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid rgba(236, 185, 202, 0.52);
                font-size: 14px;
                font-weight: 900;
                box-shadow: 0 12px 26px rgba(150, 95, 118, 0.10);
            }

            .final-login-left h1 {
                max-width: 430px;
                margin-bottom: 18px;
                color: #3f3037;
                font-size: clamp(38px, 4.6vw, 56px);
                line-height: 1.08;
                font-weight: 950;
                letter-spacing: -1.4px;
            }

            .final-login-left h1 span {
                color: #d85f8a;
            }

            .final-login-left p {
                max-width: 430px;
                margin-bottom: 0;
                color: #735d68;
                font-size: 16px;
                line-height: 1.8;
                font-weight: 650;
            }

            .final-city-box {
                position: relative;
                margin-top: 42px;
                max-width: 430px;
                height: 190px;
                overflow: hidden;
                border-radius: 28px;
                background:
                    linear-gradient(180deg, rgba(255,255,255,0.76), rgba(255,255,255,0.46)),
                    radial-gradient(circle at 88% 18%, rgba(255, 220, 125, 0.34), transparent 30%);
                border: 1px solid rgba(255, 255, 255, 0.78);
                box-shadow: 0 18px 42px rgba(150, 95, 118, 0.12);
            }

            .final-city-sun {
                position: absolute;
                top: 24px;
                right: 42px;
                width: 54px;
                height: 54px;
                border-radius: 50%;
                background: linear-gradient(135deg, #ffdc7d, #fff2b8);
                box-shadow: 0 14px 28px rgba(255, 209, 105, 0.30);
            }

            .final-city-cloud {
                position: absolute;
                top: 44px;
                left: 44px;
                width: 92px;
                height: 34px;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.88);
            }

            .final-city-cloud::before {
                content: "";
                position: absolute;
                left: 20px;
                top: -18px;
                width: 38px;
                height: 38px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.88);
            }

            .final-city-cloud::after {
                content: "";
                position: absolute;
                right: 18px;
                top: -12px;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.88);
            }

            .final-city-ground {
                position: absolute;
                left: -30px;
                right: -30px;
                bottom: -38px;
                height: 100px;
                border-radius: 50% 50% 0 0;
                background: linear-gradient(180deg, #e7f9e6, #d7f1dc);
            }

            .final-city-road {
                position: absolute;
                left: 0;
                right: 0;
                bottom: 0;
                height: 44px;
                background: linear-gradient(180deg, #d6c8ff, #c6b8ef);
            }

            .final-city-road::after {
                content: "";
                position: absolute;
                left: 50px;
                right: 50px;
                top: 20px;
                height: 4px;
                border-radius: 999px;
                background: repeating-linear-gradient(
                    90deg,
                    rgba(255, 255, 255, 0.88) 0 26px,
                    transparent 26px 48px
                );
            }

            .final-city-building {
                position: absolute;
                bottom: 42px;
                border-radius: 18px 18px 10px 10px;
                border: 3px solid rgba(255, 255, 255, 0.78);
                box-shadow: 0 14px 26px rgba(133, 80, 101, 0.13);
            }

            .final-city-building.one {
                left: 58px;
                width: 68px;
                height: 82px;
                background: linear-gradient(180deg, #f8a9c3, #ffe0ea);
            }

            .final-city-building.two {
                left: 138px;
                width: 76px;
                height: 112px;
                background: linear-gradient(180deg, #ffdc7d, #fff2bb);
            }

            .final-city-building.three {
                left: 226px;
                width: 72px;
                height: 94px;
                background: linear-gradient(180deg, #bfeaff, #e9f8ff);
            }

            .final-city-building.four {
                left: 310px;
                width: 62px;
                height: 72px;
                background: linear-gradient(180deg, #f7b7cf, #ffe6ef);
            }

            .final-city-building::before,
            .final-city-building::after {
                content: "";
                position: absolute;
                top: 18px;
                width: 10px;
                height: 12px;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.80);
            }

            .final-city-building::before {
                left: 14px;
            }

            .final-city-building::after {
                right: 14px;
            }

            .final-login-right {
                padding: 56px;
                display: flex;
                align-items: center;
                background:
                    radial-gradient(circle at 90% 10%, rgba(255, 226, 149, 0.16), transparent 28%),
                    linear-gradient(180deg, #ffffff 0%, #fffdfb 100%);
            }

            .final-login-form {
                width: 100%;
                max-width: 430px;
                margin: 0 auto;
            }

            .final-login-head {
                text-align: center;
                margin-bottom: 30px;
            }

            .final-login-icon {
                width: 68px;
                height: 68px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 16px;
                border-radius: 24px;
                background: linear-gradient(135deg, #ffe3ec, #fff2c4);
                color: #d85f8a;
                font-size: 30px;
                box-shadow: 0 14px 30px rgba(216, 95, 138, 0.14);
            }

            .final-login-head h3 {
                margin-bottom: 8px;
                color: #3f3037;
                font-size: 31px;
                font-weight: 950;
                letter-spacing: -0.7px;
            }

            .final-login-head p {
                margin-bottom: 0;
                color: #78636d;
                font-weight: 650;
                line-height: 1.6;
            }

            .final-login-form label {
                margin-bottom: 8px;
                color: #3f3037;
                font-weight: 850;
            }

            .final-input-wrap {
                position: relative;
            }

            .final-input-wrap i {
                position: absolute;
                left: 18px;
                top: 50%;
                transform: translateY(-50%);
                color: #d85f8a;
                font-size: 17px;
                z-index: 2;
            }

            .final-input-wrap .form-control {
                min-height: 54px;
                padding-left: 48px;
                border-radius: 17px;
                border: 1px solid #efcbd8;
                background: #fffafb;
                color: #3f3037;
                font-weight: 700;
                box-shadow: none;
            }

            .final-input-wrap .form-control:focus {
                border-color: #d85f8a;
                box-shadow: 0 0 0 0.22rem rgba(216, 95, 138, 0.14);
                background: #ffffff;
            }

            .final-input-wrap .form-control::placeholder {
                color: #b89da8;
                font-weight: 650;
            }

            .final-input-wrap input:-webkit-autofill,
            .final-input-wrap input:-webkit-autofill:hover,
            .final-input-wrap input:-webkit-autofill:focus {
                -webkit-text-fill-color: #3f3037;
                box-shadow: 0 0 0 1000px #fffafb inset;
                transition: background-color 5000s ease-in-out 0s;
            }

            .final-login-button {
                min-height: 54px;
                border: none;
                border-radius: 999px;
                color: #ffffff;
                background: linear-gradient(135deg, #d85f8a, #f0a0bc);
                font-weight: 950;
                box-shadow: 0 16px 32px rgba(216, 95, 138, 0.22);
                transition: 0.22s ease;
            }

            .final-login-button:hover {
                transform: translateY(-2px);
                color: #ffffff;
                background: linear-gradient(135deg, #cf527e, #ee98b5);
            }

            .final-login-note {
                margin-top: 22px;
                padding: 14px 16px;
                border-radius: 18px;
                text-align: center;
                color: #75616a;
                background: #fff8e8;
                border: 1px solid #f2ddb0;
                font-size: 14px;
                font-weight: 650;
                line-height: 1.6;
            }

            #login-alert .alert {
                border: none;
                border-radius: 16px;
                font-weight: 750;
            }

            @media (max-width: 950px) {
                .final-login-card {
                    grid-template-columns: 1fr;
                }

                .final-login-left,
                .final-login-right {
                    padding: 36px 28px;
                }

                .final-login-left h1 {
                    font-size: 38px;
                }

                .final-city-box {
                    height: 170px;
                }
            }

            @media (max-width: 560px) {
                .final-login-page {
                    padding: 28px 14px;
                }

                .final-login-card {
                    border-radius: 26px;
                }

                .final-city-box {
                    display: none;
                }
            }
        </style>

        <div class="final-login-page">
            <div class="final-login-card">
                <section class="final-login-left">
                    <div class="final-login-badge">
                        <i class="bi bi-stars"></i>
                        Citizen Portal
                    </div>

                    <h1>
                        Selamat datang di <span>LONG City</span>
                    </h1>

                    <p>
                        Masuk untuk membuat laporan, memantau status, dan ikut menjaga
                        kota tetap rapi, aman, serta nyaman.
                    </p>

                    <div class="final-city-box">
                        <div class="final-city-sun"></div>
                        <div class="final-city-cloud"></div>
                        <div class="final-city-ground"></div>

                        <div class="final-city-building one"></div>
                        <div class="final-city-building two"></div>
                        <div class="final-city-building three"></div>
                        <div class="final-city-building four"></div>

                        <div class="final-city-road"></div>
                    </div>
                </section>

                <section class="final-login-right">
                    <div class="final-login-form">
                        <div class="final-login-head">
                            <div class="final-login-icon">
                                <i class="bi bi-person-heart"></i>
                            </div>

                            <h3>Login Citizen</h3>

                            <p>
                                Masukkan akun kamu untuk mengakses portal warga.
                            </p>
                        </div>

                        <div id="login-alert"></div>

                        <form id="login-form">
                            <div class="mb-3">
                                <label for="login-username" class="form-label">
                                    Username
                                </label>

                                <div class="final-input-wrap">
                                    <i class="bi bi-person"></i>
                                    <input
                                        type="text"
                                        class="form-control"
                                        id="login-username"
                                        placeholder="Masukkan username"
                                        required
                                    >
                                </div>
                            </div>

                            <div class="mb-4">
                                <label for="login-password" class="form-label">
                                    Password
                                </label>

                                <div class="final-input-wrap">
                                    <i class="bi bi-lock"></i>
                                    <input
                                        type="password"
                                        class="form-control"
                                        id="login-password"
                                        placeholder="Masukkan password"
                                        required
                                    >
                                </div>
                            </div>

                            <button type="submit" class="btn final-login-button w-100">
                                <i class="bi bi-box-arrow-in-right me-1"></i>
                                Login
                            </button>
                        </form>

                        <div class="final-login-note">
                            LONG City siap menjadi kota yang lebih bersih, rapi, dan nyaman.
                        </div>
                    </div>
                </section>
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