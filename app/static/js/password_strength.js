/*jshint esversion: 6 */
document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('password');
    const passwordStrengthBar = document.getElementById('passwordStrengthBar');
    const passwordStrengthText = document.getElementById('passwordStrengthText');
    const signUpButton = document.getElementById('signUpButton');

    passwordInput.addEventListener('input', function () {
        const strength = getPasswordStrength(passwordInput.value);
        passwordStrengthText.textContent = `Password Strength: ${strength.label}`;
        updatePasswordStrengthBar(strength.score);
        updatePasswordStrengthColor(strength.label);
        signUpButton.disabled = (strength.label === 'Weak');
    });

    //https://stackoverflow.com/questions/50547523/how-can-i-use-javascript-to-test-for-password-strength-in-a-way-that-returns-the
    function getPasswordStrength(password) {
        let score = 0;
        let strength = 'Weak';

        const patterns = [
            /[a-z]/,
            /[A-Z]/,
            /[0-9]/,
            /[^a-zA-Z0-9]/
        ];

        const matches = patterns.filter(pattern => pattern.test(password)).length;

        if (password.length >= 8) {
            score = matches * 25;
            switch (matches) {
                case 4:
                    strength = 'Very Strong';
                    break;
                case 3:
                    strength = 'Strong';
                    break;
                case 2:
                    strength = 'Medium';
                    break;
                default:
                    strength = 'Weak';
                    break;
            }
        }
        return { score, label: strength };
    }

    function updatePasswordStrengthBar(score) {
        passwordStrengthBar.style.width = `${score}%`;
    }

    function updatePasswordStrengthColor(strength) {
        switch (strength) {
            case 'Very Strong':
                passwordStrengthBar.classList.add('bg-success');
                passwordStrengthBar.classList.remove('bg-warning', 'bg-danger');
                break;
            case 'Strong':
                passwordStrengthBar.classList.add('bg-info');
                passwordStrengthBar.classList.remove('bg-success', 'bg-warning', 'bg-danger');
                break;
            case 'Medium':
                passwordStrengthBar.classList.add('bg-warning');
                passwordStrengthBar.classList.remove('bg-success', 'bg-info', 'bg-danger');
                break;
            default:
                passwordStrengthBar.classList.add('bg-danger');
                passwordStrengthBar.classList.remove('bg-success', 'bg-info', 'bg-warning');
        }
    }
});
