//containsNumberValidator
export function passwordHasNumberValidator(password: string): null | string {
    //Define const variables
    const cleanedPassword = password.trim().toLowerCase()
    const passwordNumberPattern = /[0-9]/;

    //Condition to check against validation rule
    if (passwordNumberPattern.test(cleanedPassword)) {
        return null;
    }
    return "The password must contain at least one number.";
};

//specialCharacersValidator
export function passwordHasSpecialCharacterValidator(password: string): null | string {
    //Define const variables
    const cleanedPassword = password.trim().toLowerCase()
    const passwordSpecialCharacterPattern = /[!@#$%^&*]/;

    //Condition to check against validation rule
    if (passwordSpecialCharacterPattern.test(cleanedPassword)) {
        return null;
    }
    return "The password must contain at least one special character.";
};

//uppperCaseValidator
export function passwordHasUpperCaseValidator(password: string): null | string {
    //Define const variables
    const cleanedPassword = password.trim()
    const passwordUpperCasePattern = /[A-Z]/;

    //Condition to check against validation rule
    if (passwordUpperCasePattern.test(cleanedPassword)) {
        return null;
    }
    return "The password must contain at least one upper case letter.";
};

//minimumLengthValidator
export function passwordminimumLengthValidator(password: string): null | string {
    //Define const variables
    const cleanedPassword = password.trim()
    const lenCleanedPassword = cleanedPassword.length

    //Condition to check against validation rule
    if (lenCleanedPassword >= 8) {
        return null;
    }
    return "The password must contain at least 8 characters.";
};

//orchestration function
export function orchestratePasswordValidator(password: string): string[] | null {
    //Define empty array for error messages 
    const errorMessages: string[] = [];

    //Call password validator functions
    const numberError = passwordHasNumberValidator(password);
    const specialCharError = passwordHasSpecialCharacterValidator(password);
    const upperCaseError = passwordHasUpperCaseValidator(password);
    const minLengthError = passwordminimumLengthValidator(password);

    if (numberError) errorMessages.push(numberError);
    if (specialCharError) errorMessages.push(specialCharError);
    if (upperCaseError) errorMessages.push(upperCaseError);
    if (minLengthError) errorMessages.push(minLengthError);

    return errorMessages.length > 0 ? errorMessages : null;

};


//Integrate these functions into HTML page + Django form
document.addEventListener("DOMContentLoaded", (): void => {
    //Define const variables
    const form = document.getElementById("auth-form") as HTMLFormElement;
    const passwordError = document.getElementById("password-error") as HTMLDivElement;

    //Get all passwordFields
    const passwordFields: NodeListOf<HTMLInputElement> = 
        form.querySelectorAll<HTMLInputElement>('input[type="password"]');

    //Check that all const exist
    if (!form || passwordFields.length === 0 || !passwordError) {
        console.warn('Required elements not found:', {
            form: !!form,
            passwordFieldsCount: passwordFields.length,
            passwordError: !!passwordError
        });
        return;
    }

    //Perform validation on form once user clicks "submit"
    form.addEventListener("submit", (event: SubmitEvent): void => {
        let hasErrors = false;
        const allErrors: string[] = [];

        // Validate each password field
        passwordFields.forEach((field: HTMLInputElement): void => {
            const errors = orchestratePasswordValidator(field.value);

            if (errors) {
                hasErrors = true;
                allErrors.push(...errors);

            }
        });

        // Handle validation results
        if (hasErrors) {
            event.preventDefault(); // Stop Django form submission
            
            //Clean errors by de-duplicating them
            const cleanedErrors = [...new Set(allErrors)]
            passwordError.innerHTML = cleanedErrors.join('<br>'); // Display all errors
        } else {
            passwordError.textContent = ""; // Clear errors
        }
    });

    console.log('passwordValidator initialized');
});