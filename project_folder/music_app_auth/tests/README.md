# Overview
This README provides an outline of the testing process, its importance, and guidelines on how to run tests specifically for the music_app

## What is Covered

* Django tests:
    * There a total of 11 unit tests related to testing the functionalities in django
    * Test modules: 
        * test_models
        * test_views

* Common code tests:
    * There a total of 4 unit tests related to testing the backends.py module
    * Test modules: 
        * test_email_backend

## How to Run the Test

* Django tests:
In your terminal, run the following command:
`docker compose up -d`
`docker compose exec web python manage.py makemigrations`
`docker compose exec web python manage.py migrate`
`docker compose exec web python manage.py test --settings=music_app_main.settings_test`
