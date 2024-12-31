import re
from django.core.exceptions import ValidationError

def validate_username_format(value):
    if not all(c.isalnum() or c in " ._- " for c in value):  # Erlaubte Zeichen prüfen
        raise ValidationError(
            'Only alphanumeric characters, spaces, hyphens, and underscores are allowed.',
            code='invalid'
        )

def validate_phone_format(value):
    phone_regex = r'^\+?[0-9\s\-]+$'
    if not re.match(phone_regex, value):
        raise ValidationError("Phone number only allows numbers, spaces, and hyphens.")
    
    if len(value) < 6:
        raise ValidationError("Phone number must be at least 6 characters.")