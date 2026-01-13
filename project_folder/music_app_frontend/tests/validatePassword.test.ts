import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as password_validators from '../src/validatePassword';

//Test passwordHasNumberValidator function
describe('passwordHasNumberValidator', () => {
    it('returns null for valid passwords', () => {
        expect(password_validators.passwordHasNumberValidator('Meep!234')).toBeNull();
    });

    it('returns an error message for invalid passwords', () => {
        expect(password_validators.passwordHasNumberValidator('Meep!@#$')).toBe(
            "The password must contain at least one number."
        );
    });

    it('Trims the whitespaces before validating', () => {
        expect(password_validators.passwordHasNumberValidator('    Meep!234.   ')).toBeNull();
    });
});


//Test passwordHasSpecialCharacterValidator function
describe('passwordHasSpecialCharacterValidator', () => {
    it('returns null for valid passwords', () => {
        expect(password_validators.passwordHasSpecialCharacterValidator('Meep!$%')).toBeNull();
    });

    it('returns an error message for invalid passwords', () => {
        expect(password_validators.passwordHasSpecialCharacterValidator('Meep123')).toBe(
            "The password must contain at least one special character."
        );
    });

    it('Trims the whitespaces before validating', () => {
        expect(password_validators.passwordHasSpecialCharacterValidator('    Meep!234.   ')).toBeNull();
    });
});


//Test passwordHasUpperCaseValidator function
describe('passwordHasUpperCaseValidator', () => {
    it('returns null for valid passwords', () => {
        expect(password_validators.passwordHasUpperCaseValidator('Meep!$%')).toBeNull();
    });

    it('returns an error message for invalid passwords', () => {
        expect(password_validators.passwordHasUpperCaseValidator('meep123')).toBe(
            "The password must contain at least one upper case letter."
        );
    });

    it('Trims the whitespaces before validating', () => {
        expect(password_validators.passwordHasUpperCaseValidator('    Meep!234.   ')).toBeNull();
    });
});


//Test passwordminimumLengthValidator function
describe('passwordminimumLengthValidator', () => {
    it('returns null for valid passwords', () => {
        expect(password_validators.passwordminimumLengthValidator('longPassword')).toBeNull();
    });

    it('returns an error message for invalid passwords', () => {
        expect(password_validators.passwordminimumLengthValidator('short')).toBe(
            "The password must contain at least 8 characters."
        );
    });

    it('Trims the whitespaces before validating', () => {
        expect(password_validators.passwordminimumLengthValidator('    longPassword   ')).toBeNull();
    });

    it('Trims the whitespaces before validating and still fails', () => {
        expect(password_validators.passwordminimumLengthValidator('    short   ')).toBe(
            "The password must contain at least 8 characters."
        );
    });
});


//Test orchestratePasswordValidator function
describe('orchestratePasswordValidator', () => {
    it('returns null for valid passwords', () => {
        const errors = password_validators.orchestratePasswordValidator('Meep!234');
        expect(errors).toBeNull();
    });

    it('returns an error message for invalid passwords', () => {
        expect(password_validators.orchestratePasswordValidator('Sh0rt$')).toContain(
            "The password must contain at least 8 characters."
        );
    });

    it('returns multiple error messages for invalid passwords', () => {
        const errors = password_validators.orchestratePasswordValidator('Sh0rt');
        expect(errors).not.toBeNull();
        expect(errors).toContain("The password must contain at least 8 characters.");
        expect(errors).toContain("The password must contain at least one special character.");    
    });

    it('Trims the whitespaces before validating', () => {
        const errors = password_validators.orchestratePasswordValidator('    Meep!234   ');
        expect(errors).toBeNull();
    });

    it('Trims the whitespaces before validating and still fails', () => {
        const errors = password_validators.orchestratePasswordValidator('    Sh0rt$   ')
        expect(errors).not.toBeNull();
        expect(errors).toContain("The password must contain at least 8 characters.");
    });
});


//Test DOM integration with form submission
describe('password validation on form submit', () => {
    let form: HTMLFormElement;
    let passwordInput: HTMLInputElement;
    let passwordErrorDiv: HTMLDivElement;

    beforeEach(() => {
        // Set up DOM
        document.body.innerHTML = `
            <form id="auth-form">
                <input id="id_password1" type="password" />
                <div id="password-error"></div>
                <button type="submit">Submit</button>
            </form>
        `;

        form = document.getElementById('auth-form') as HTMLFormElement;
        passwordInput = document.getElementById('id_password1') as HTMLInputElement;
        passwordErrorDiv = document.getElementById('password-error') as HTMLDivElement;

        form.addEventListener("submit", (event: SubmitEvent): void => {
            const errors = password_validators.orchestratePasswordValidator(passwordInput.value);

            if (errors) {
                event.preventDefault();
                passwordErrorDiv.innerHTML = errors.join('<br>');
            } else {
                passwordErrorDiv.textContent = "";
            }
        });
    });

    it('prevents submission and displays errors for invalid password', () => {
        // Set invalid password
        passwordInput.value = "Sh0rt";

        // Create and dispatch submit event
        const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
        const preventDefaultSpy = vi.spyOn(submitEvent, 'preventDefault');

        form.dispatchEvent(submitEvent);

        // Assertions
        expect(preventDefaultSpy).toHaveBeenCalled(); // Form submission prevented
        expect(passwordErrorDiv.innerHTML).toContain("The password must contain at least 8 characters.");
        expect(passwordErrorDiv.innerHTML).toContain("The password must contain at least one special character.");
    });

    it('allows submission and clears errors for valid password', () => {
        // Set valid password
        passwordInput.value = "Meep!234";

        // Create and dispatch submit event
        const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
        const preventDefaultSpy = vi.spyOn(submitEvent, 'preventDefault');

        form.dispatchEvent(submitEvent);

        // Assertions
        expect(preventDefaultSpy).not.toHaveBeenCalled(); // Form submission NOT prevented
        expect(passwordErrorDiv.textContent).toBe(""); // Errors cleared
    });

    it('displays multiple errors in the error div', () => {
        passwordInput.value = "fail";

        const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
        form.dispatchEvent(submitEvent);

        // Check that multiple errors are displayed
        const errorHTML = passwordErrorDiv.innerHTML;
        expect(errorHTML).toContain("The password must contain at least 8 characters.");
        expect(errorHTML).toContain("The password must contain at least one number.");
        expect(errorHTML).toContain("The password must contain at least one special character.");
        expect(errorHTML).toContain("The password must contain at least one upper case letter.");
    });
}); 