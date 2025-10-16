# music_app

## Overview

**music_app** is a Django-based web application for a music platform. This is code I have taken from my private repo. I will build this in stages.

I'm building the back-end first, once the features work as expected I'll begin with improving the front-end.

## Developer notes:
Coming soon:
  - More unit tests to be written
  - Create user profile. As well as 'The archive',for creating playlists.
  - Containerise the app in Docker

## Features

- **User Authentication**
  - Custom user model (email as primary identifier)
  - Registration with email verification
  - Secure login/logout
  - Password reset via email

- **Forms & Validation**
  - Custom form validation for better UX
  - Custom password validators
  - JS-powered “show password” toggle

- **Error Handling**
  - Centralized custom exception classes (`src/custom_exceptions.py`)
  - Reusable error-handling utilities (`src/django_error_utils.py`)

## Project Structure
```
project_folder/
├── manage.py
├── environment.yml
├── README.md                 # Main project README
├── music_app/                # Main Django app
│   ├── admin.py
│   ├── apps.py
│   ├── asgi.py
│   ├── changelog.md
│   ├── forms.py
│   ├── managers.py
│   ├── models.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── wsgi.py
│   ├── templates/
│   ├── static/
│   └── tests/
│       ├── test_email_backend.py
│       ├── test_models.py
│       └── test_views.py
├── common/                   # Shared logic and utilities
│   ├── backends.py
│   ├── send_email.py
│   ├── utils.py
│   ├── validators.py
│   └── README.md
├── src/                      # Cross-cutting project-wide modules
│   ├── custom_exceptions.py
│   ├── django_error_utils.py
│   └── README.md
└── static/
    └── music_app/
        └── show_password.js
```


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
- **Install Homebrew** (if not already installed):
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

- **Install Miniconda**:
    ```bash
    brew install --cask miniconda
    ```

3. **Software dependencies:**
- **Create Conda Environment**:
    ```bash
    conda env create -f ./environment.yml -n music_app
    ```
- **Update Conda Environment**:
    ```bash
    conda env update --name music_app --file ./environment.yml --prune
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
