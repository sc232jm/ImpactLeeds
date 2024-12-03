/*jshint esversion: 6 */
document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
        e.preventDefault();
        const petitionId = this.getAttribute('data-id');

        // Derived from: https://sweetalert2.github.io/#ajax-request
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            // Utilising AJAX with documentation from: https://stackoverflow.com/questions/43523321/writing-a-ajax-post-http-request
            if (result.isConfirmed) {
                $.ajax({
                    url: '{{ url_for("delete_petition") }}',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({petition_id: petitionId}),
                    success: function () {
                        Swal.fire(
                            'Deleted!',
                            'Your petition has been deleted.',
                            'success'
                        ).then(() => {
                            location.reload();
                        });
                    },
                    error: function () {
                        Swal.fire(
                            'Error!',
                            'There was an error deleting your petition.',
                            'error'
                        );
                    }
                });
            }
        });
    });
});