"""
Custom Exceptions
"""


class ApplicationError(Exception):
    """Base application error"""
    pass


class AuthenticationError(ApplicationError):
    """Authentication failed"""
    pass


class AuthorizationError(ApplicationError):
    """User not authorized"""
    pass


class NotFoundError(ApplicationError):
    """Resource not found"""
    pass


class ValidationError(ApplicationError):
    """Invalid data"""
    pass


class BusinessRuleError(ApplicationError):
    """Business rule violation"""
    pass

