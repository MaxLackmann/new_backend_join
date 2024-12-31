import re
from django.core.exceptions import ValidationError

def validate_username_format(value):
    if not all(c.isalnum() or c in " ._- " for c in value):
        raise ValidationError(
            'Use only letters, numbers, spaces, "-", and "_".',
            code='invalid'
        )

def validate_phone_format(value):
    phone_regex = r'^\+?[0-9\s\-]+$'
    if not re.match(phone_regex, value):
        raise ValidationError("Invalid phone number format.")
    
    if len(value) < 6:
        raise ValidationError("Phone number too short.")