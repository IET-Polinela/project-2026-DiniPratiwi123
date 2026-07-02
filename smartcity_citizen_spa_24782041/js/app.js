let currentTab = 'my_reports';
let currentPage = 1;
let editingReportId = null;
const DEFAULT_PAGE_SIZE = 10;

document.addEventListener('DOMContentLoaded', function () {
    if (!window.location.hash) {
        window.location.hash = '#login';
    }

    updateNavbar();
    setupReportModalEvents();
});

function setupReportModalEvents() {
    const reportForm = document.getElementById('report-form');
    const saveDraftButton = document.getElementById('save-draft-button');
    const submitReportButton = document.getElementById('submit-report-button');

    if (reportForm) {
        reportForm.addEventListener('submit', function (event) {
            event.preventDefault();
        });
    }

    if (saveDraftButton) {
        saveDraftButton.addEventListener('click', function () {
            saveReport(false);
        });
    }

    if (submitReportButton) {
        submitReportButton.addEventListener('click', function () {
            saveReport(true);
        });
    }
}

function initDashboard() {
    currentTab = 'my_reports';
    currentPage = 1;
    loadDashboardData(currentTab, currentPage);
}

async function loadDashboardData(tab = 'my_reports', page = 1) {
    if (!localStorage.getItem('access_token')) {
        window.location.hash = '#login';
        return;
    }

    currentTab = tab;
    currentPage = page;

    setActiveTab(tab);
    showDashboardAlert('');

    const reportList = document.getElementById('report-list');

    if (reportList) {
        reportList.innerHTML = `
            <div class="col-12">
                <div class="card dashboard-card p-4 text-center text-muted">
                    Memuat data laporan...
                </div>
            </div>
        `;
    }

    const result = await requestAPI(`/api/report/?tab=${tab}&page=${page}`, 'GET');

    if (!result.ok) {
        if (result.status === 401) {
            logoutCitizen();
            return;
        }

        renderList([]);
        renderPagination(null);
        showDashboardAlert('Gagal mengambil data laporan dari server.', 'danger');
        return;
    }

    const paginatedData = result.data;
    const reports = Array.isArray(paginatedData.results) ? paginatedData.results : [];

    renderList(reports);
    renderPagination(paginatedData);

    await loadSummaryStats();
}

async function loadSummaryStats() {
    const result = await requestAPI('/api/report/?tab=my_reports&page_size=1000', 'GET');

    if (!result.ok) {
        updateSummaryElement('summary-draft', 0);
        updateSummaryElement('summary-reported', 0);
        updateSummaryElement('summary-verified', 0);
        updateSummaryElement('summary-progress', 0);
        updateSummaryElement('summary-resolved', 0);
        return;
    }

    const reports = Array.isArray(result.data.results) ? result.data.results : [];

    const totalDraft = reports.filter(function (report) {
        return report.status === 'DRAFT';
    }).length;

    const totalReported = reports.filter(function (report) {
        return report.status === 'REPORTED';
    }).length;

    const totalVerified = reports.filter(function (report) {
        return report.status === 'VERIFIED';
    }).length;

    const totalProgress = reports.filter(function (report) {
        return report.status === 'IN_PROGRESS';
    }).length;

    const totalResolved = reports.filter(function (report) {
        return report.status === 'RESOLVED';
    }).length;

    updateSummaryElement('summary-draft', totalDraft);
    updateSummaryElement('summary-reported', totalReported);
    updateSummaryElement('summary-verified', totalVerified);
    updateSummaryElement('summary-progress', totalProgress);
    updateSummaryElement('summary-resolved', totalResolved);
}

function updateSummaryElement(elementId, value) {
    const element = document.getElementById(elementId);

    if (element) {
        element.textContent = value;
    }
}

function renderList(reports) {
    const reportList = document.getElementById('report-list');

    if (!reportList) {
        return;
    }

    if (!reports || reports.length === 0) {
        reportList.innerHTML = `
            <div class="col-12">
                <div class="card dashboard-card p-4 text-center text-muted">
                    Belum ada laporan di tab ini.
                </div>
            </div>
        `;
        return;
    }

    reportList.innerHTML = reports.map(function (report) {
        return renderReportCard(report);
    }).join('');
}

function renderReportCard(report) {
    const progress = getStatusProgress(report.status);
    const createdAt = formatDate(report.created_at);
    const updatedAt = formatDate(report.updated_at);
    const actionButtons = renderActionButtons(report);

    return `
        <div class="col-12 col-xl-6">
            <div class="card report-card h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="badge ${progress.badgeClass}">
                            ${progress.label}
                        </span>
                        <small class="small-muted">
                            ${escapeHTML(report.category || '-')}
                        </small>
                    </div>

                    <h5 class="fw-bold mb-2">
                        ${escapeHTML(report.title || '-')}
                    </h5>

                    <p class="report-description mb-3">
                        ${escapeHTML(report.description || '-')}
                    </p>

                    <hr>

                    <p class="mb-1">
                        <strong>Lokasi:</strong>
                        ${escapeHTML(report.location || '-')}
                    </p>

                    <p class="mb-1">
                        <strong>Oleh:</strong>
                        ${escapeHTML(report.reporter || 'Warga Anonim')}
                    </p>

                    <p class="small-muted small mb-2">
                        Dibuat: ${createdAt} | Diperbarui: ${updatedAt}
                    </p>

                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <small class="fw-semibold">Progress Laporan</small>
                        <small class="fw-semibold" style="color:#b85f81;">
                            ${progress.progressText} (${progress.percent}%)
                        </small>
                    </div>

                    <div class="progress mb-3">
                        <div
                            class="progress-bar ${progress.progressClass}"
                            role="progressbar"
                            style="width: ${progress.percent}%"
                            aria-valuenow="${progress.percent}"
                            aria-valuemin="0"
                            aria-valuemax="100">
                        </div>
                    </div>

                    ${actionButtons}
                </div>
            </div>
        </div>
    `;
}

function renderActionButtons(report) {
    const isEditableDraft = (
        currentTab === 'my_reports' &&
        report.status === 'DRAFT' &&
        report.is_owner === true
    );

    if (!isEditableDraft) {
        return '';
    }

    return `
        <div class="d-flex gap-2 flex-wrap">
            <button type="button" class="btn btn-outline-primary btn-sm" onclick="editDraft(${report.id})">
                <i class="bi bi-pencil-square me-1"></i>
                Edit
            </button>

            <button type="button" class="btn btn-primary btn-sm" onclick="submitDraft(${report.id})">
                <i class="bi bi-send-fill me-1"></i>
                Ajukan
            </button>

            <button type="button" class="btn btn-outline-danger btn-sm" onclick="deleteDraft(${report.id})">
                <i class="bi bi-trash me-1"></i>
                Hapus
            </button>
        </div>
    `;
}

function renderPagination(paginatedData) {
    const paginationContainer = document.getElementById('pagination-container');

    if (!paginationContainer) {
        return;
    }

    if (!paginatedData || !paginatedData.count) {
        paginationContainer.innerHTML = '';
        return;
    }

    const totalPages = Math.ceil(paginatedData.count / DEFAULT_PAGE_SIZE);

    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }

    let paginationHTML = `<nav aria-label="Pagination laporan"><ul class="pagination pagination-sm flex-wrap justify-content-center mb-0">`;

    paginationHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <button type="button" class="page-link" onclick="loadDashboardData('${currentTab}', ${currentPage - 1})">
                Sebelumnya
            </button>
        </li>
    `;

    const pagesToShow = buildPaginationPages(currentPage, totalPages);

    pagesToShow.forEach(function (page) {
        if (page === '...') {
            paginationHTML += `
                <li class="page-item disabled">
                    <span class="page-link">...</span>
                </li>
            `;
        } else {
            paginationHTML += `
                <li class="page-item ${page === currentPage ? 'active' : ''}">
                    <button type="button" class="page-link" onclick="loadDashboardData('${currentTab}', ${page})">
                        ${page}
                    </button>
                </li>
            `;
        }
    });

    paginationHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <button type="button" class="page-link" onclick="loadDashboardData('${currentTab}', ${currentPage + 1})">
                Selanjutnya
            </button>
        </li>
    `;

    paginationHTML += `</ul></nav>`;

    paginationContainer.innerHTML = paginationHTML;
}

function buildPaginationPages(current, total) {
    const pages = [];

    if (total <= 7) {
        for (let i = 1; i <= total; i++) {
            pages.push(i);
        }
        return pages;
    }

    pages.push(1);

    if (current > 4) {
        pages.push('...');
    }

    const start = Math.max(2, current - 1);
    const end = Math.min(total - 1, current + 1);

    for (let i = start; i <= end; i++) {
        pages.push(i);
    }

    if (current < total - 3) {
        pages.push('...');
    }

    pages.push(total);

    return pages;
}

function setActiveTab(tab) {
    const myReportsTab = document.getElementById('tab-my-reports');
    const feedTab = document.getElementById('tab-feed');

    if (myReportsTab) {
        myReportsTab.classList.toggle('active', tab === 'my_reports');
    }

    if (feedTab) {
        feedTab.classList.toggle('active', tab === 'feed');
    }
}

function getStatusProgress(status) {
    const statusMap = {
        DRAFT: {
            label: 'DRAFT',
            progressText: 'Draft',
            percent: 0,
            badgeClass: 'bg-secondary',
            progressClass: 'bg-secondary',
        },
        REPORTED: {
            label: 'REPORTED',
            progressText: 'Diajukan',
            percent: 25,
            badgeClass: 'bg-warning',
            progressClass: 'bg-warning',
        },
        VERIFIED: {
            label: 'VERIFIED',
            progressText: 'Diverifikasi',
            percent: 50,
            badgeClass: 'bg-info',
            progressClass: 'bg-info',
        },
        IN_PROGRESS: {
            label: 'IN PROGRESS',
            progressText: 'Diproses',
            percent: 75,
            badgeClass: 'bg-primary',
            progressClass: 'bg-primary',
        },
        RESOLVED: {
            label: 'RESOLVED',
            progressText: 'Selesai',
            percent: 100,
            badgeClass: 'bg-success',
            progressClass: 'bg-success',
        },
    };

    return statusMap[status] || {
        label: status || 'UNKNOWN',
        progressText: 'Tidak diketahui',
        percent: 0,
        badgeClass: 'bg-dark',
        progressClass: 'bg-dark',
    };
}

function openCreateReportModal() {
    editingReportId = null;

    const reportForm = document.getElementById('report-form');
    const modalTitle = document.getElementById('reportModalLabel');

    if (reportForm) {
        reportForm.reset();
    }

    if (modalTitle) {
        modalTitle.innerHTML = `<i class="bi bi-pencil-square me-2"></i>Buat Laporan Baru`;
    }

    showModalAlert('');
    showReportModal();
}

async function editDraft(id) {
    editingReportId = id;

    const result = await requestAPI(`/api/report/${id}/`, 'GET');

    if (!result.ok) {
        showDashboardAlert('Gagal mengambil data draft untuk diedit.', 'danger');
        return;
    }

    const report = result.data;

    if (report.status !== 'DRAFT') {
        showDashboardAlert('Hanya laporan berstatus DRAFT yang dapat diedit.', 'warning');
        return;
    }

    document.getElementById('report-title').value = report.title || '';
    document.getElementById('report-category').value = report.category || '';
    document.getElementById('report-location').value = report.location || '';
    document.getElementById('report-description').value = report.description || '';

    const modalTitle = document.getElementById('reportModalLabel');

    if (modalTitle) {
        modalTitle.innerHTML = `<i class="bi bi-pencil-square me-2"></i>Edit Draft Laporan`;
    }

    showModalAlert('');
    showReportModal();
}

async function saveReport(shouldSubmit) {
    const payload = getReportPayload();

    if (!payload.title || !payload.category || !payload.location || !payload.description) {
        showModalAlert('Semua field laporan wajib diisi.', 'warning');
        return;
    }

    setModalButtonsDisabled(true);

    const endpoint = editingReportId === null ? '/api/report/' : `/api/report/${editingReportId}/`;
    const method = editingReportId === null ? 'POST' : 'PUT';

    const result = await requestAPI(endpoint, method, payload);

    if (!result.ok || (result.status !== 200 && result.status !== 201)) {
        setModalButtonsDisabled(false);
        showModalAlert(getErrorMessage(result.data), 'danger');
        return;
    }

    const savedReport = result.data;

    if (shouldSubmit) {
        const submitResult = await requestAPI(`/api/report/${savedReport.id}/submit/`, 'POST');

        if (!submitResult.ok || submitResult.status !== 200) {
            setModalButtonsDisabled(false);
            showModalAlert(getErrorMessage(submitResult.data), 'danger');
            return;
        }
    }

    closeReportModal();
    resetReportFormState();

    await loadDashboardData('my_reports', 1);

    if (shouldSubmit) {
        showDashboardAlert('Laporan berhasil diajukan.', 'success');
    } else {
        showDashboardAlert('Draft laporan berhasil disimpan.', 'success');
    }

    setModalButtonsDisabled(false);
}

async function submitDraft(id) {
    const confirmation = confirm('Ajukan draft laporan ini? Setelah diajukan, laporan tidak dapat diedit lagi oleh citizen.');

    if (!confirmation) {
        return;
    }

    const result = await requestAPI(`/api/report/${id}/submit/`, 'POST');

    if (!result.ok || result.status !== 200) {
        showDashboardAlert(getErrorMessage(result.data), 'danger');
        return;
    }

    await loadDashboardData('my_reports', 1);
    showDashboardAlert('Draft berhasil diajukan menjadi laporan.', 'success');
}

async function deleteDraft(id) {
    const confirmation = confirm('Hapus draft laporan ini? Draft yang sudah dihapus tidak dapat dikembalikan.');

    if (!confirmation) {
        return;
    }

    const result = await requestAPI(`/api/report/${id}/`, 'DELETE');

    if (!result.ok || result.status !== 204) {
        showDashboardAlert(getErrorMessage(result.data), 'danger');
        return;
    }

    await loadDashboardData('my_reports', 1);
    showDashboardAlert('Draft laporan berhasil dihapus.', 'success');
}

function getReportPayload() {
    return {
        title: document.getElementById('report-title').value.trim(),
        category: document.getElementById('report-category').value.trim(),
        location: document.getElementById('report-location').value.trim(),
        description: document.getElementById('report-description').value.trim(),
    };
}

function resetReportFormState() {
    const reportForm = document.getElementById('report-form');

    if (reportForm) {
        reportForm.reset();
    }

    editingReportId = null;
    showModalAlert('');
}

function showReportModal() {
    const modalElement = document.getElementById('reportModal');

    if (!modalElement) {
        return;
    }

    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.show();
}

function closeReportModal() {
    const modalElement = document.getElementById('reportModal');

    if (!modalElement) {
        return;
    }

    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.hide();
}

function setModalButtonsDisabled(isDisabled) {
    const saveDraftButton = document.getElementById('save-draft-button');
    const submitReportButton = document.getElementById('submit-report-button');

    if (saveDraftButton) {
        saveDraftButton.disabled = isDisabled;
    }

    if (submitReportButton) {
        submitReportButton.disabled = isDisabled;
    }
}

function showDashboardAlert(message, type = 'primary') {
    const alertBox = document.getElementById('dashboard-alert');

    if (!alertBox) {
        return;
    }

    if (!message) {
        alertBox.innerHTML = '';
        return;
    }

    alertBox.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${escapeHTML(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Tutup"></button>
        </div>
    `;
}

function showModalAlert(message, type = 'primary') {
    const alertBox = document.getElementById('report-form-alert');

    if (!alertBox) {
        return;
    }

    if (!message) {
        alertBox.innerHTML = '';
        return;
    }

    alertBox.innerHTML = `
        <div class="alert alert-${type}" role="alert">
            ${escapeHTML(message)}
        </div>
    `;
}

function getErrorMessage(data) {
    if (!data) {
        return 'Terjadi kesalahan saat memproses request.';
    }

    if (typeof data.detail === 'string') {
        return data.detail;
    }

    if (typeof data.status === 'string') {
        return data.status;
    }

    if (typeof data === 'string') {
        return data;
    }

    return 'Request gagal diproses. Periksa kembali data laporan.';
}

function formatDate(value) {
    if (!value) {
        return '-';
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return '-';
    }

    return date.toLocaleString('id-ID', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

function escapeHTML(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}