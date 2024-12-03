/*jshint esversion: 6 */

/* Utilising SweetAlert2 */
/* Documentation obtained from: https://sweetalert2.github.io/#usage */

function display(flashMessages) {
    // Loop through each message, extracting the category and content
    flashMessages.forEach(message => {
        const [category, text] = message;
        if (category === 'success') {
            // If the content includes TOAST send the alert as a toast
            if (text.includes('TOAST')) {
                const Toast = Swal.mixin({
                    toast: true,
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true,
                });
                Toast.fire({
                    icon: text.includes("ERRTOAST") ? "error" : "success",
                    title: text.split("|")[1]
                });
            } else {
                // Otherwise send standard alert
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: text,
                    timer: 2000,
                    showConfirmButton: false
                });
            }
        } else {
            // Send an error
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: text
            });
        }
    });
}
// Read the flash-message attribute to check for any new messages
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = JSON.parse(document.getElementById('flash-messages').textContent);
    if (flashMessages.length > 0) {
        // Call the display function to display the messages
        display(flashMessages);
    }
});
