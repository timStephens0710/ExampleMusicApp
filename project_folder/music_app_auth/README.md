# Music App — User Authentication Module

This Django project implements a secure and fully-featured user authentication workflow for the **Music App**. It includes:

- User registration with email verification  
- Login & logout  
- Forgotten password + reset password system  
- One-time token generation and validation  
- Extensive application logging  
- Custom exception handling  
- Email-based flows (authentication + password reset)

---

## Table of Contents
1. [Overview](#overview)  
2. [Features](#features)  
3. [Application Flow](#application-flow)  
4. [One-Time Token System](#one-time-token-system)  
5. [Views Summary](#views-summary)  
6. [Project Structure](#project-structure)  
7. [Requirements](#requirements)  
8. [How to Run](#how-to-run)  
9. [Email Templates](#email-templates)  
10. [Logging](#logging)  
11. [Error Handling](#error-handling)
11. [Testing](#testing)


---

## Overview

This module provides a secure, logged, token-based authentication system for the **Music App**. It replaces the default Django auth flow with an email-driven workflow:

- Users register and must verify their email before logging in.  
- Users authenticate through time-limited, single-use tokens.  
- Password resets also rely on securely generated one-time tokens.  
- All critical events are logged through the `AppLogging` model.

---

## Features

- Email verification  
- Token-based password reset  
- Custom user model (`CustomUser`)  
- Centralised exception handling  
- Detailed logging via `AppLogging`  
- Resend-token functionality  
- CSRF-protected Django forms  
- User-friendly error pages  

---

## Application Flow

### 1. Registration
1. User completes the sign-up form (`RegistrationForm`).  
2. Account is created in an unverified state.  
3. A one-time authentication token is generated.  
4. User receives an email containing a verification link.  
5. User is redirected to a "check your email" page.

---

### 2. Email Verification
1. User clicks the verification link.  
2. Token is validated → marked used → deactivated.  
3. User's `email_verified` flag is set to `True`.  
4. User sees a success confirmation page.  
5. A new token can be requested if the original expires.

---

### 3. Login
The login process:

- Users authenticate using **email + password**.  
- Errors handled via custom exceptions:
  - `EmailNotFound`  
  - `IncorrectPassword`  
  - `UnverifiedEmail`

These are shown to the user via Django messages.

---

### 4. Forgotten Password
1. User enters their email.  
2. A reset-password token is generated.  
3. User receives an email with a secure link.  
4. Redirected to a "check your email" page.  
5. Option to request a new token.

---

### 5. Reset Password
1. User clicks the reset link.  
2. Token is validated and marked used.  
3. User submits a new password.  
4. Success page displayed.

---

## One-Time Token System

The `OneTimeToken` model manages authentication and password-reset tokens. Tokens include the following fields:

- `token`  
- `purpose` (`AUTH` or `RESET_PASSWORD`)  
- `is_used`  
- `is_active`  
- `created_on`  

### Token lifecycle
1. Created → Active / Unused  
2. Used once → Marked Used and Inactive  
3. Resent → Old token deactivated, new token generated  

---

## Views Summary

### Public Views

| View | Purpose |
|------|---------|
| `home` | Landing page |
| `user_registration` | Register user + send verification email |
| `user_authentication` | "Check email" page + resend authentication email |
| `user_authentication_success` | Email verification confirmation |
| `user_login` | Sign in using email and password |
| `user_logout` | Logout confirmation |
| `user_forgotten_password` | Request password reset |
| `check_your_email_password` | "Check email" page for password reset |
| `user_reset_password` | Set new password (token protected) |
| `user_success_reset_password` | Password reset success screen |

---

## Project Structure

```
music_app_auth/
├── migrations/                  # Database migrations
│   └── ...
│
├── src/                        # Business logic and utilities
│   ├── custom_exceptions.py    # Custom exception classes
│   └── django_error_utils.py   # Error handling utilities
│
├── common/                     # Shared utilities
│   ├── backends.py            # Custom authentication backend
│   ├── utils.py               # Token generation utilities
│   ├── validators.py          # Custom validators
│   └── send_email.py          # Email sending functionality
│
├── views/                      # View controllers
│   ├── app_views.py           # Application-specific views
│   └── main_views.py          # Core authentication views
│
├── tests/                      # Test suite
│   ├── test_email_backend.py # Email backend tests
│   ├── test_models.py         # Model tests
│   └── test_views.py          # View tests
│
├── templates/                  # HTML templates
│   ├── authentication_email.html
│   ├── reset_password_email.html
│   └── ...
│
├── models.py                   # Database models (CustomUser, OneTimeToken, AppLogging)
├── forms.py                    # Django forms (RegistrationForm, LoginForm, etc.)
├── managers.py                 # Custom model managers
├── admin.py                    # Django admin configuration
├── urls.py                     # URL routing
└── README.md                   # This file
```

---

## Requirements

Refer to `environment.yml` for full package dependencies.

**Key Dependencies:**
- Email backend (SMTP configuration)

---

## How to Run

### 1. Make migrations
```bash
python manage.py makemigrations
```

### 2. Apply migrations
```bash
python manage.py migrate
```

### 3. Create a superuser (optional)
```bash
python manage.py createsuperuser
```

### 4. Start the server
```bash
python manage.py runserver
```

App available at: **http://127.0.0.1:8000/**

---

## Email Templates

Required email templates (located in `templates/`):

### `authentication_email.html`
Sent when user registers.

**Expected context:**
- `username` - User's username
- `authentication_link` - Email verification URL

### `reset_password_email.html`
Sent when user requests password reset.

**Expected context:**
- `username` - User's username
- `reset_password_link` - Password reset URL

---

## Logging

The project logs all major events via the `AppLogging` model, including:

- Registration submissions
- Authentication email sent
- Password reset requested
- Tokens deactivated
- Password successfully changed

This enables auditability and debugging.

**Log Entry Format:**
```python
AppLogging.objects.create(
    user_id=user.id,
    log_text="User registered successfully"
)
```

---

## Error Handling

Errors are handled using the custom error handler in:

```
src/django_error_utils.py
```

This system:
- Captures unexpected exceptions
- Builds context for the template
- Renders a clean `error_page.html`
- Custom exceptions help guide users with clear, user-friendly messages

### Custom Exceptions

Defined in `src/custom_exceptions.py`:

```python
class EmailNotFound(Exception):
    """Raised when email doesn't exist in database"""
    pass

class IncorrectPassword(Exception):
    """Raised when password is incorrect"""
    pass

class UnverifiedEmail(Exception):
    """Raised when user tries to login with unverified email"""
    pass
```

---

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test music_app_auth

# Run specific test file
python manage.py test music_app_auth.tests.test_views

# Run with coverage
coverage run --source='.' manage.py test music_app_auth
coverage report
```

---

## Security Considerations

- One-time tokens expire after use
- Tokens are time-limited (configurable)
- Passwords are hashed using Django's default hasher
- CSRF protection on all forms
- Email verification required before login
- Secure token generation using secrets module

---