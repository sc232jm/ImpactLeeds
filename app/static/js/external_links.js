/*jshint esversion: 6 */
document.addEventListener('DOMContentLoaded', function () {
    const externalLinks = document.querySelectorAll('a[href^="http"]');

    externalLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            Swal.fire({
                title: 'Redirecting to an external site',
                text: `You are being redirected to: ${link.href}. Do you want to proceed?`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, proceed!',
                cancelButtonText: 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = link.href;
                }
            });
        });
    });
});
