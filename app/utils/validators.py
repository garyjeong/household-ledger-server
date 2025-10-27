"""
Validators
Utility functions for data validation
"""

import re
from typing import Optional


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_password(password: str) -> bool:
    """Validate password strength"""
    # At least 8 characters, one letter, one number
    if len(password) < 8:
        return False
    if not re.search(r'[a-zA-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True


def is_valid_nickname(nickname: str) -> bool:
    """Validate nickname"""
    # No special characters except spaces
    if len(nickname) < 1 or len(nickname) > 60:
        return False
    return True

