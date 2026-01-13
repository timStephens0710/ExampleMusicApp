/**
 * Password Toggle Functionality
 * Toggles visibility of password fields when checkbox is clicked
 */

document.addEventListener('DOMContentLoaded', (): void => {
  const checkboxes: NodeListOf<HTMLInputElement> = 
    document.querySelectorAll<HTMLInputElement>('.show-password-toggle');

  checkboxes.forEach((checkbox: HTMLInputElement): void => {
    const form: HTMLFormElement | null = checkbox.closest('form');
    
    if (!form) {
      console.warn('No form found for password toggle');
      return;
    }

    // Cache password fields on initialization (they're still type="password")
    const passwordFields: NodeListOf<HTMLInputElement> = 
      form.querySelectorAll<HTMLInputElement>('input[type="password"]');

    if (passwordFields.length === 0) {
      console.warn('No password fields found in form');
      return;
    }

    // Add event listener with cached fields
    checkbox.addEventListener('change', (): void => {
      passwordFields.forEach((field: HTMLInputElement): void => {
        field.type = checkbox.checked ? 'text' : 'password';
      });
    });
  });

  console.log('Password toggle initialized');
});