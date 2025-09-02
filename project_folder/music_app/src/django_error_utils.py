import logging
import inspect
from django.http import Http404
from django.core.exceptions import ValidationError, PermissionDenied

logger = logging.getLogger(__name__)

def handle_django_error(error):
    """
    This function will: Log the error, categorise it, and prepare context for rendering the error page.

    Args:
        error (Exception): The exception that was raised.

    Returns:
        additional_context: additional error context to be added to the error_page.
    """
    # Get the name of the caller function
    func_name = inspect.currentframe().f_back.f_code.co_name

    # Categorize the error
    # More error can be introduced later on 
    if isinstance(error, Http404):
        category = "Resource Not Found"
        message = f"The requested resource could not be found while calling {func_name}. Please check whether the requested URL is correct."
    elif isinstance(error, AttributeError):
        category = "Attribute Error"
        message = f"An unexpected error occurred while calling {func_name}."
    elif isinstance(error, TypeError):
        category = "Type Error"
        message = f"A type error occurred while calling {func_name}."
    else:
        category = "General Error"
        message = f"An unexpected error occurred while calling {func_name}."
    
    # Log the error with the category and function name
    logger.error(f"{category} in {func_name}: {error}")

    # Prepare context for the error page
    additional_context = {
        'function_name': func_name,
        'error_category': category,
        'message': message,
        'error_text': str(error)
    }
    return additional_context