document.addEventListener('DOMContentLoaded', function () {
    if (!window.location.hash) {
        window.location.hash = '#login';
    }

    updateNavbar();
});