/*jshint esversion: 8 */


/* Utilising nprogress to improve visuals */
/* Code obtained from: https://github.com/rstacruz/nprogress?tab=readme-ov-file#basic-usage */
document.addEventListener('DOMContentLoaded', function () {
    NProgress.start();
});

// Stop NProgress when window finishes loading
window.addEventListener('load', function () {
    NProgress.done();
});

// Start NProgress on AJAX request
$(document).ajaxStart(function () {
    NProgress.start();
});

// Stop NProgress on AJAX request completion
$(document).ajaxComplete(function () {
    NProgress.done();
});