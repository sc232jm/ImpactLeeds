/*jshint esversion: 6 */
function display(flashMessages) {
    flashMessages.forEach(message => {
        console.log(message)
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
                    icon: "success",
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
    };
});
