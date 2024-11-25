/*jshint esversion: 6 */
document.addEventListener('DOMContentLoaded', (event) => {
    const flashMessages = JSON.parse(document.getElementById('flash-messages').textContent);
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            const [category, text] = message;
            if (category === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: text,
                    timer: 2000,
                    showConfirmButton: false
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: text
                });
            }
        });
    }
});
