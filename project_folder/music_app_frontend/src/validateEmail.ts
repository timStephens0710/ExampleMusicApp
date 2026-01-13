//Create function that validates email address
export function checkEmailIsValid(email: string): null | string {
    //Define const variables
    const trimmedEmail = email.trim().toLowerCase();
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com$/;

    //Condition to check against validation rule
    if (emailPattern.test(trimmedEmail)) {
        return null;
    }
    return "The e-mail address is not valid. It must contain '@' and '.com'.";
};


//Integrate with the HTML page + Django form
document.addEventListener("DOMContentLoaded", () => {
    //Define const variables
    const form = document.getElementById("auth-form") as HTMLFormElement;
    const emailInput = document.getElementById("id_email") as HTMLInputElement;
    const emailError = document.getElementById("email-error") as HTMLDivElement;

    //Check that all const exist
    if (!form || !emailInput || !emailError) {
        console.warn('Required elements not found:', {
            form: !!form,
            emailInput: !!emailInput,
            emailError: !!emailError
        });
        return;
    }

    //Perform validation on form once user clicks "submits"
    form.addEventListener("submit", (event: SubmitEvent) => {
        const error = checkEmailIsValid(emailInput.value);

        if (error) {
            event.preventDefault(); //stop the Django form submission
            emailError.textContent = error;
        } else {
            emailError.textContent = "";
        }
    });
      console.log('validateEmail initialized');
});