import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

   
class ContainsNumberValidator:
    '''
    The following validator class ensures the user sets a password contains at least one number.
    Otherwise they receive the get_help_text.
    '''
    def __init__(self, min_number=1):
        self.min_number = min_number

    def validate(self, password, user=None):
        if sum(char.isdigit() for char in password) < self.min_number:
            raise ValidationError(
                _('The password must contain at least %(min_number)d number(s).'),
                code='password_no_numbers',
                params={'min_number': self.min_number},
            )

    def get_help_text(self):
        return _(
            'Your password must contain at least %(min_number)d number(s).'
        ) % {'min_number': self.min_number}
    

class SpecialCharacterValidator:
    '''
    The following validator class ensures the user sets a password contains at least one symbol/special character.
    Otherwise they receive the get_help_text.
    '''
    def __init__(self, min_symbols=1, symbols="!@#$%^&*()_+{}[]:;\"'<>,.?/\\|-"):
        self.min_symbols = min_symbols
        self.symbols = symbols

    def validate(self, password, user=None):
        found_symbols = [char for char in password if char in self.symbols]
        if len(found_symbols) < self.min_symbols:
            raise ValidationError(
                _("Your password must contain at least %(min_symbols)d special character(s)."),
                code='password_no_special_characters',
                params={'min_symbols': self.min_symbols},
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(min_symbols)d special character(s) from: %(symbols)s."
        ) % {'min_symbols': self.min_symbols, 'symbols': self.symbols}