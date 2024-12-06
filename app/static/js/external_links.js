/*jshint esversion: 8 */
document.addEventListener('DOMContentLoaded', function () {
    // Find all links on the current page
    // https://stackoverflow.com/questions/56782843/problem-with-document-queryselectorall-ahref-is-not-a-valid-selector
    const externalLinks = document.querySelectorAll('a[href^="http"]');

    externalLinks.forEach(function (link) {
        // Attach a click listener to the link object and prevent the default behaviour
        link.addEventListener('click', function (event) {
            event.preventDefault();
            // Utilising SweetAlert2
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
                // Redirect the user if they agree to proceed
                if (result.isConfirmed) {
                    window.location.href = link.href;
                }
            });
        });
    });
});
