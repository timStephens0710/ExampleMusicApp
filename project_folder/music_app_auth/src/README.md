# SRC FOLDER

The src/ folder contains project-level core utilities that are responsible for error handling and custom exceptions.

Unlike common/, which contains reusable helpers and utilities, the src/ folder focuses on cross-project error resilience and exception management. This helps ensure that your project fails gracefully and provides meaningful feedback to developers and users.

It contains the following modules:
* custom_exceptions.py
* django_error_utils

### Best Practices

Keep exceptions declarative: one class per specific error scenario.

Extend Django’s built-in exceptions (ValidationError, PermissionDenied, etc.) when possible to stay consistent.

Use handle_django_error() as a single point of failure handling in your views so that all unexpected errors get logged and displayed consistently.

Keep error messages user-friendly, while logging should remain developer-friendly with technical details.