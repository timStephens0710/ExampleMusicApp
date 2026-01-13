interface RegistraionForm {
    email: string;
    username: string;
    password1: string; 
    password2: string;
}

interface LoginForm {
    email: string;
    password: string;
}

interface ForgottenPasswordForm {
    email: string;
}

interface ResetPasswordForm {
    newPassword1: string;
    newPassword2: string;
}