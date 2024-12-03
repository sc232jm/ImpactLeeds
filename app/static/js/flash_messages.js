/*jshint esversion: 6 */

/* Utilising SweetAlert2 */
/* Documentation obtained from: https://sweetalert2.github.io/#usage */

function display(flashMessages) {
    flashMessages.forEach(message => {
        const [category, text] = message;
        if (category === 'success') {
            if (text.includes('TOAST')) {
                const Toast = Swal.mixin({
                    toast: true,
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true,
                    didOpen: (toast) => {
                        toast.onmouseenter = Swal.stopTimer;
                        toast.onmouseleave = Swal.resumeTimer;
                    }
                    });
                    Toast.fire({
                    icon: text.includes("ERRTOAST") ? "error" : "success",
                    title: text.split("|")[1]
                    });
            } else {
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: text,
                    timer: 2000,
                    showConfirmButton: false
                });
            }
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: text
            });
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = JSON.parse(document.getElementById('flash-messages').textContent);
    if (flashMessages.length > 0) {
        display(flashMessages);
    }
});
