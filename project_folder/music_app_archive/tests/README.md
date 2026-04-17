# Overview
This README provides an outline of the testing process, its importance, and guidelines on how to run tests specifically for the music_app_archive

## What is Covered

* Django tests:
    * There a total of 94 unit tests related to testing the functionalities in django
    * Test modules: 
        * test_integrations
        * test_models
        * test_views
        * test_services
        * test_utils


## How to Run the Test

* Django tests:
In your terminal, run the following commands:
`docker compose up -d`
`docker compose exec web python manage.py makemigrations`
`docker compose exec web python manage.py migrate`
`docker compose exec web python manage.py test --settings=music_app_main.settings_test`


## When I'm ready to go more CI
services:
  db:
    container_name: postgres_db
    image: postgres:16
    restart: always
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    env_file:
      - .env.dev
    environment:
      - POSTGRES_DB=music_app_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  selenium:
    container_name: selenium_chrome
    image: selenium/standalone-chromium:latest
    restart: always
    shm_size: 725mb
    ports:
      - "4444:4444"
      - "7900:7900"
    environment:
      - SE_NODE_MAX_SESSIONS=5
      - SE_NODE_SESSION_TIMEOUT=300

  web:
    container_name: django_web
    build:
      context: .
      target: backend-dev
    restart: always
    command: >
      bash -c "python manage.py migrate
      && python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/project_folder
      - static_volume:/project_folder/staticfiles
    env_file:
      - .env.dev
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_started
      selenium:
        condition: service_started
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/music_app_db
      - SELENIUM_REMOTE_URL=http://selenium:4444

  test:                                        
    container_name: music_app_pytest
    build:
      context: .
      target: backend-dev
    command: pytest
    volumes:
      - .:/project_folder
    env_file:
      - .env.dev
    profiles:                                  
      - test
    depends_on:
      db:
        condition: service_started
      selenium:
        condition: service_started
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/music_app_db
      - SELENIUM_REMOTE_URL=http://selenium:4444

volumes:
  postgres_data:
  static_volume: