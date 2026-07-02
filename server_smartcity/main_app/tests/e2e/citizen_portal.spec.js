const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://127.0.0.1:8000';
const SPA_URL = 'http://127.0.0.1:5500/index.html';

const VALID_ACCESS_TOKEN = 'fake.valid.access.token';
const EXPIRED_ACCESS_TOKEN = 'fake.expired.access.token';
const EXPIRED_REFRESH_TOKEN = 'fake.expired.refresh.token';

const TEST_ADMIN_USERNAME = 'admin';
const TEST_ADMIN_PASSWORD = 'admin123';

async function setupAuthTokens(page, accessToken = VALID_ACCESS_TOKEN, refreshToken = EXPIRED_REFRESH_TOKEN) {
    await page.evaluate(({ access, refresh }) => {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        localStorage.setItem('citizen_username', 'testwarga');
    }, { access: accessToken, refresh: refreshToken });
}

async function clearAuthTokens(page) {
    await page.evaluate(() => localStorage.clear());
}

async function loginAdmin(page) {
    await page.goto(`${BASE_URL}/users/login/`);
    await page.waitForSelector('form', { state: 'visible', timeout: 10000 });

    await page.locator('input[name="username"]').fill(TEST_ADMIN_USERNAME);
    await page.locator('input[name="password"]').fill(TEST_ADMIN_PASSWORD);

    await Promise.all([
        page.waitForLoadState('networkidle'),
        page.locator('button[type="submit"], input[type="submit"]').first().click(),
    ]);
}

function mockReportList(page, total = 25) {
    const reports = [];

    for (let i = 1; i <= total; i++) {
        reports.push({
            id: i,
            title: `Laporan Test ${i}`,
            category: i % 2 === 0 ? 'Infrastruktur' : 'Kebersihan',
            description: `Deskripsi laporan nomor ${i}`,
            location: `Lokasi ${i}`,
            status: i % 5 === 0 ? 'RESOLVED' : 'REPORTED',
            reporter: 'Warga Anonim',
            is_owner: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
        });
    }

    return page.route('**/api/report/**', async (route) => {
        const request = route.request();
        const method = request.method();
        const url = request.url();

        if (method === 'POST') {
            const postData = request.postDataJSON();

            await route.fulfill({
                status: 201,
                contentType: 'application/json',
                body: JSON.stringify({
                    id: 999,
                    title: postData.title,
                    category: postData.category,
                    description: postData.description,
                    location: postData.location,
                    status: 'DRAFT',
                    reporter: 'testwarga',
                    is_owner: true,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                }),
            });
            return;
        }

        if (url.includes('page_size=1000')) {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    count: 1,
                    results: [{
                        id: 999,
                        title: 'Draft Baru',
                        category: 'Infrastruktur',
                        description: 'Draft test',
                        location: 'Lab',
                        status: 'DRAFT',
                        reporter: 'testwarga',
                        is_owner: true,
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                    }],
                }),
            });
            return;
        }

        const pageMatch = url.match(/page=(\d+)/);
        const pageNum = pageMatch ? Number(pageMatch[1]) : 1;
        const pageSize = 10;
        const start = (pageNum - 1) * pageSize;
        const end = start + pageSize;

        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                count: reports.length,
                next: end < reports.length ? 'next' : null,
                previous: pageNum > 1 ? 'previous' : null,
                results: reports.slice(start, end),
            }),
        });
    });
}

test.describe('Modul 1: Otorisasi & Sesi SPA', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto(SPA_URL);
        await clearAuthTokens(page);
    });

    test('AUTH-04: akses #dashboard tanpa token redirect ke #login', async ({ page }) => {
        await page.goto(`${SPA_URL}#dashboard`);

        await page.waitForFunction(() => window.location.hash === '#login', null, { timeout: 5000 });

        await expect(page).toHaveURL(/#login/);
        await expect(page.locator('#login-form')).toBeVisible();
    });

    test('AUTH-05: API 401 membersihkan sesi dan redirect ke login', async ({ page }) => {
        await setupAuthTokens(page, EXPIRED_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);

        await page.route('**/api/report/**', async (route) => {
            await route.fulfill({
                status: 401,
                contentType: 'application/json',
                body: JSON.stringify({ detail: 'Token invalid' }),
            });
        });

        await page.goto(`${SPA_URL}#dashboard`);

        await page.waitForFunction(() => window.location.hash === '#login', null, { timeout: 10000 });

        await expect(page.locator('#login-form')).toBeVisible();

        const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
        const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));

        expect(accessToken).toBeNull();
        expect(refreshToken).toBeNull();
    });

    test('AUTH-06: kedua token expired membuat user kembali ke login', async ({ page }) => {
        await setupAuthTokens(page, EXPIRED_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);

        await page.route('**/api/report/**', async (route) => {
            await route.fulfill({
                status: 401,
                contentType: 'application/json',
                body: JSON.stringify({ detail: 'Token expired' }),
            });
        });

        await page.goto(`${SPA_URL}#dashboard`);

        await page.waitForFunction(() => window.location.hash === '#login', null, { timeout: 10000 });

        await expect(page).toHaveURL(/#login/);
        await expect(page.locator('#login-form')).toBeVisible();

        const username = await page.evaluate(() => localStorage.getItem('citizen_username'));
        expect(username).toBeNull();
    });
});

test.describe('Modul 5: Interaktivitas UI', () => {
    test('UI-01: Chart.js dashboard admin ter-render', async ({ page }) => {
        await loginAdmin(page);

        await page.goto(`${BASE_URL}/dashboard/`);
        await page.waitForLoadState('networkidle');

        await expect(page.locator('#statusChart')).toBeVisible({ timeout: 15000 });
        await expect(page.locator('#categoryChart')).toBeVisible({ timeout: 15000 });

        const statusBox = await page.locator('#statusChart').boundingBox();
        const categoryBox = await page.locator('#categoryChart').boundingBox();

        expect(statusBox.width).toBeGreaterThan(0);
        expect(statusBox.height).toBeGreaterThan(0);
        expect(categoryBox.width).toBeGreaterThan(0);
        expect(categoryBox.height).toBeGreaterThan(0);

        await expect(page.locator('#latestReportedTable')).toBeVisible();
        await expect(page.locator('#latestResolvedTable')).toBeVisible();
    });

    test('UI-02: Live search daftar laporan admin berjalan', async ({ page }) => {
        await loginAdmin(page);

        await page.goto(`${BASE_URL}/reports/`);
        await page.waitForLoadState('networkidle');

        const searchInput = page.locator('#liveSearchInput');
        const tableBody = page.locator('#reportTableBody');

        await expect(searchInput).toBeVisible();
        await expect(tableBody).toBeVisible();

        const responsePromise = page.waitForResponse(
            response =>
                response.url().includes('/api/reports/search/?q=Lampu') &&
                response.status() === 200,
            { timeout: 15000 }
        );

        await searchInput.fill('Lampu');

        const response = await responsePromise;
        const data = await response.json();

        expect(Array.isArray(data.reports)).toBe(true);

        await page.waitForTimeout(700);

        const rowCount = await tableBody.locator('tr').count();
        expect(rowCount).toBeGreaterThan(0);
    });

    test('UI-03: Feed Kota maksimal menampilkan 10 kartu dan pagination muncul', async ({ page }) => {
        await page.goto(SPA_URL);
        await mockReportList(page, 25);
        await setupAuthTokens(page);

        await page.goto(`${SPA_URL}#dashboard`);

        await expect(page.locator('button:has-text("Buat Laporan Baru")')).toBeVisible({ timeout: 10000 });

        await page.locator('#tab-feed').click();
        await page.waitForTimeout(1000);

        const cardCount = await page.locator('#report-list .report-card').count();

        expect(cardCount).toBeGreaterThan(0);
        expect(cardCount).toBeLessThanOrEqual(10);

        await expect(page.locator('#pagination-container')).toBeVisible();

        const paginationCount = await page.locator('#pagination-container .page-item').count();
        expect(paginationCount).toBeGreaterThanOrEqual(3);
    });

    test('UI-04: tombol Buat Laporan Baru membuka modal', async ({ page }) => {
        await page.goto(SPA_URL);
        await mockReportList(page, 0);
        await setupAuthTokens(page);

        await page.goto(`${SPA_URL}#dashboard`);

        const openModalButton = page.locator('button:has-text("Buat Laporan Baru")');
        await expect(openModalButton).toBeVisible({ timeout: 10000 });

        await expect(page.locator('#reportModal')).not.toBeVisible();

        await openModalButton.click();

        await expect(page.locator('#reportModal')).toBeVisible();
        await expect(page.locator('#report-form')).toBeVisible();
        await expect(page.locator('#report-title')).toBeVisible();
        await expect(page.locator('#report-category')).toBeVisible();
        await expect(page.locator('#report-location')).toBeVisible();
        await expect(page.locator('#report-description')).toBeVisible();
        await expect(page.locator('#save-draft-button')).toBeVisible();
        await expect(page.locator('#submit-report-button')).toBeVisible();
    });

    test('UI-05: simpan draft menutup modal dan badge draft bertambah', async ({ page }) => {
        await page.goto(SPA_URL);
        await mockReportList(page, 0);
        await setupAuthTokens(page);

        await page.goto(`${SPA_URL}#dashboard`);

        await page.locator('button:has-text("Buat Laporan Baru")').click();
        await expect(page.locator('#reportModal')).toBeVisible();

        await page.locator('#report-title').fill('AC Mati di Lab CPS 1');
        await page.locator('#report-category').selectOption('Infrastruktur');
        await page.locator('#report-location').fill('Gedung Lab Analisis Lantai 2');
        await page.locator('#report-description').fill('AC tidak berfungsi sejak pagi dan mengganggu praktikum.');

        await page.locator('#save-draft-button').click();

        await expect(page.locator('#reportModal')).not.toBeVisible({ timeout: 10000 });
        await expect(page.locator('#dashboard-alert')).toContainText('Draft laporan berhasil disimpan', { timeout: 10000 });

        const draftCount = Number(await page.locator('#summary-draft').textContent());
        expect(draftCount).toBeGreaterThanOrEqual(1);
    });

    test('UI-06: navbar responsif pada viewport mobile', async ({ page }) => {
        await page.setViewportSize({ width: 400, height: 800 });

        await page.goto(SPA_URL);
        await page.waitForLoadState('domcontentloaded');

        await expect(page.locator('.navbar')).toBeVisible();

        const toggler = page.locator('.navbar-toggler');
        await expect(toggler).toBeVisible();

        const collapse = page.locator('#navbarMenu');
        const hasShowClass = await collapse.evaluate(el => el.classList.contains('show'));

        expect(hasShowClass).toBe(false);
    });
});
