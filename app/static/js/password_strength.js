/*jshint esversion: 8 */
document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('password');
    const passwordStrengthFill = document.getElementById('passwordStrengthFill');
    const signUpButton = document.getElementById('signUpButton');

    passwordInput.addEventListener('input', function () {
        const password = passwordInput.value;
        const percentage = updatePasswordCriteria(password);

        // Update the bar's width and color
        updatePasswordStrengthBar(percentage);

        // Enable/Disable the button
        signUpButton.disabled = percentage < 75;
    });

    // Define the password criteria using REGEX
    function updatePasswordCriteria(password) {
        const criteria = [
            { id: 'criteriaLength', pattern: /.{8,}/ },
            { id: 'criteriaLowercase', pattern: /[a-z]/ },
            { id: 'criteriaUppercase', pattern: /[A-Z]/ },
            { id: 'criteriaNumber', pattern: /[0-9]/ },
            { id: 'criteriaSpecial', pattern: /[^a-zA-Z0-9]/ },
        ];

        let matches = 0;

        criteria.forEach(criterion => {
            const element = document.getElementById(criterion.id);
            if (criterion.pattern.test(password)) {
                element.style.display = 'none'; // Hide satisfied requirement
                matches++;
            } else {
                element.style.display = 'block'; // Show unsatisfied requirement
            }
        });

        // Calculate percentage based on the number of satisfied criteria
        return (matches / criteria.length) * 100;
    }

    function updatePasswordStrengthBar(percentage) {
        passwordStrengthFill.style.width = `${percentage}%`;

        // Change the bar's color based on strength
        if (percentage === 100) {
            passwordStrengthFill.style.backgroundColor = '#28a745'; // Green
        } else if (percentage >= 80) {
            passwordStrengthFill.style.backgroundColor = '#ffc107'; // Yellow
        } else if (percentage >= 60) {
            passwordStrengthFill.style.backgroundColor = '#fd7e14'; // Orange
        } else {
            passwordStrengthFill.style.backgroundColor = '#dc3545'; // Red
        }
    }
});
