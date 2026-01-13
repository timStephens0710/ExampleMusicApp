import { describe, it, expect, beforeEach, vi } from 'vitest';
import { checkEmailIsValid } from '../src/validateEmail';

//Test checkEmailIsValid function
describe('checkEmailIsValid', () => {
  it('returns null for valid emails', () => {
    expect(checkEmailIsValid('test@example.com')).toBeNull();
    expect(checkEmailIsValid('michael.selfish92@domain.com')).toBeNull();
  });

  it('returns an error message for invalid emails', () => {
    expect(checkEmailIsValid('invalid-email')).toBe(
      "The e-mail address is not valid. It must contain '@' and '.com'."
    );
    expect(checkEmailIsValid('no-at-sign.com')).toBe(
      "The e-mail address is not valid. It must contain '@' and '.com'."
    );
  });

  it('trims whitespace and lowercases before validating', () => {
    expect(checkEmailIsValid('  TEST@EXAMPLE.COM  ')).toBeNull();
  });
});


//Test DOM integration
describe('email validation on form submit', () => {
  let form: HTMLFormElement;
  let emailInput: HTMLInputElement;
  let emailErrorDiv: HTMLDivElement;

  beforeEach(() => {
    // Set up DOM
    document.body.innerHTML = `
      <form id="auth-form">
        <input id="id_email" type="email" />
        <div id="email-error"></div>
        <button type="submit">Submit</button>
      </form>
    `;

    form = document.getElementById('auth-form') as HTMLFormElement;
    emailInput = document.getElementById('id_email') as HTMLInputElement;
    emailErrorDiv = document.getElementById('email-error') as HTMLDivElement;

    // Attach your event listener (mimicking your actual integration code)
    form.addEventListener("submit", (event: SubmitEvent): void => {
      const error = checkEmailIsValid(emailInput.value);

      if (error) {
        event.preventDefault();
        emailErrorDiv.textContent = error;
      } else {
        emailErrorDiv.textContent = "";
      }
    });
  });

  it('prevents submission and displays error for invalid email', () => {
    // Set invalid email
    emailInput.value = 'bademail';

    // Create and dispatch submit event
    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
    const preventDefaultSpy = vi.spyOn(submitEvent, 'preventDefault');

    form.dispatchEvent(submitEvent);

    // Assertions
    expect(preventDefaultSpy).toHaveBeenCalled(); // Form submission prevented
    expect(emailErrorDiv.textContent).toBe(
      "The e-mail address is not valid. It must contain '@' and '.com'."
    );
  });

  it('allows submission and clears errors for valid email', () => {
    // Set valid email
    emailInput.value = 'valid@example.com';

    // Create and dispatch submit event
    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
    const preventDefaultSpy = vi.spyOn(submitEvent, 'preventDefault');

    form.dispatchEvent(submitEvent);

    // Assertions
    expect(preventDefaultSpy).not.toHaveBeenCalled(); // Form submission NOT prevented
    expect(emailErrorDiv.textContent).toBe(""); // Errors cleared
  });

  it('displays error for email without @', () => {
    emailInput.value = 'notemail.com';

    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
    form.dispatchEvent(submitEvent);

    expect(emailErrorDiv.textContent).toContain("must contain '@'");
  });

  it('displays error for email without .com', () => {
    emailInput.value = 'test@example';

    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
    form.dispatchEvent(submitEvent);

    expect(emailErrorDiv.textContent).toContain("'.com'");
  });

  it('handles empty email input', () => {
    emailInput.value = '';

    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
    const preventDefaultSpy = vi.spyOn(submitEvent, 'preventDefault');

    form.dispatchEvent(submitEvent);

    // Depending on your validation logic:
    // If empty should show error:
    expect(preventDefaultSpy).toHaveBeenCalled();
    expect(emailErrorDiv.textContent).not.toBe("");
  });
});