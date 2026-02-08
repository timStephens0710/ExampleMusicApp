# Overview
This README provides an outline of the testing process, its importance, and guidelines on how to run tests specifically for the music_app_archive

## What is Covered

* Django tests:
    * There a total of 83 unit tests related to testing the functionalities in django
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
