# COMMON FOLDER

The common/ folder contains reusable utilities, helpers, and shared logic that are not tied to a single Django app (e.g. music_app).

Its purpose is to keep the project organized by separating cross-cutting concerns (like email handling, validators, authentication backends, etc.) from the business logic of the main app.

It contains the following modules:
* backends.py
* send_email
* utils.py
* validators.py


### Best Practices

Keep this folder lightweight and generic. Anything that directly depends on models/views/templates of music_app should stay inside music_app/.

Each file should have a single responsibility (e.g. don’t mix email logic with validators).

Add unit tests for each utility to ensure they remain reliable when reused.