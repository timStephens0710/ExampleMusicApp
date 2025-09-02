# music_app

## Overview

**music_app** is a Django-based web application for a music platform. This is code I have taken from my private repo. I will build this in stages.

I'm building the back-end first, once the features work as expected I'll begin with the front-end

## Developer notes:
- More unit tests to be written.
- Feature: user can request authentication email to be.
- Front-end improvements to make it more appealing.

## Features

- **User Authentication**
  - Custom user model (email as primary identifier)
  - Registration with email verification
  - Secure login/logout
  - Password reset via email

- **Forms & Validation**
  - Custom form validation for better UX
  - JS-powered “show password” toggle

- **Error Handling**
  - Centralized custom exception classes (`src/custom_exceptions.py`)
  - Reusable error-handling utilities (`src/django_error_utils.py`)

## Project Structure
project_folder/
│
├── music_app/                  # Main Django app
│   ├── common/                 # Shared logic and utilities
│   │   ├── backends.py
│   │   ├── send_email.py
│   │   ├── utils.py
│   │   ├── validators.py
│   │   └── README.md
│   │
│   ├── migrations/
│   ├── src/                    # Cross-cutting project-wide modules
│   │   ├── custom_exceptions.py
│   │   ├── django_error_utils.py
│   │   └── README.md
│   │
│   ├── tests/
│       ├── test_email_backend.py/
│       ├── test_models.py/
│       ├── test_views.py/
│   ├── templates/
│   │
│   ├── apps.py
│   ├── admin.py
│   ├── asgi.py
│   ├── changelog.md
│   ├── models.py
│   ├── managers.py
│   ├── views.py
│   ├── settings.py
│   ├── forms.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── templates/
│   ├── static/
│   └── README.md
│   ├── static/
│   │   ├── music_app
│   │       ├── show_password.js
├── manage.py
├── environment.yml
├── README.md #this file


## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript (progressive TypeScript integration)
- **Database:** SQLite (development), configurable for PostgreSQL/MySQL
- **Testing:** Django Test Framework (unit & integration tests)

## Setup & Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/ExampleMusicApp.git
    cd music_app
    ```

2. **Mac - Create and activate a virtual environment:**
**Install Homebrew** (if not already installed):
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

**Install Miniconda**:
    ```bash
    brew install --cask miniconda
    ```

3. **Software dependencies:**
**Create Conda Environment**:
    ```bash
    conda env create -f ./project_folder/environment.yml -n music_app
    ```
**Update Conda Environment**:
    ```bash
    conda env update --name music_app --file ./project_folder/environment.yml --prune
    ```

4. **Run database migrations:**
    ```sh
    python manage.py migrate
    ```

5. **Create a superuser (admin):**
    ```sh
    python manage.py createsuperuser
    ```

6. **Start the server:**
    ```sh
    python manage.py runserver
    ```

7. **Open your browser at:**
    ```
    http://127.0.0.1:8000/
    ```

## Testing

To run tests for the app:

```sh
python manage.py test music_app