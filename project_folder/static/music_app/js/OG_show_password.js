let message = "Hello the show_password file is connected :)";
console.log(message);


document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll('.show-password-toggle');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const form = checkbox.closest('form');
            if (!form) return;

            const passwordFields = form.querySelectorAll('input[data-password]');

            passwordFields.forEach(field => {
                field.type = checkbox.checked ? 'text' : 'password';
            });
        });
    });
});