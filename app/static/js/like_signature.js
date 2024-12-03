/*jshint esversion: 6 */

document.querySelectorAll('.like-button').forEach(button => {
    button.addEventListener('click', function () {
        const signatureId = this.getAttribute('data-signature-id');
        const likeButton = this;

        // Utilising AJAX with documentation from: https://stackoverflow.com/questions/43523321/writing-a-ajax-post-http-request
        $.ajax({
            url: `/signature/${signatureId}/like`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Solved using: https://stackoverflow.com/questions/74529995/ajax-request-doesnt-send-x-requested-with-header-doest-send-no-jquery
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function (data) {
                if (data.success) {
                    const likeCountSpan = likeButton.querySelector('.like-count');
                    likeCountSpan.innerText = data.like_count;

                    const heartIcon = likeButton.querySelector('.fa-heart');
                    heartIcon.classList.toggle('fas');
                    heartIcon.classList.toggle('far');

                    let message = data.message === 'added' ? 'TOAST|Added Like' : 'TOAST|Removed Like'
                    display([['success', message]]);
                }
            }
        });
    });
});