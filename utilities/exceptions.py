from rest_framework.exceptions import APIException

from .constants import OrderItExceptions



class AuthenticationError(APIException):
    """
    AuthenticationError Exception represents an error generated during authentication
    of an account.
    """

    authenticationError = OrderItExceptions.authentication_error()

    status_code = authenticationError.get("code")
    detail = authenticationError.get("message")
    default_code = authenticationError.get("name")

    def __init__(self, message=None):
        if message:
            self.detail = message

    def __str__(self):
        str(self.detail)

class NotFoundError(APIException):
    """
    NotFoundError Exception represents an error generated when a requested resource
    is not found.
    """

    notFoundError = OrderItExceptions.not_found_error()

    status_code = notFoundError.get("code")
    detail = notFoundError.get("message")
    default_code = notFoundError.get("name")

    def __init__(self, message=None):
        if message:
            self.detail = message

    def __str__(self):
        str(self.detail)

class BadRequestError(APIException):
    """
    BadRequestError represents an error generarted when the client provides
    an invalid input.
    """

    badRequestError = OrderItExceptions.bad_request_error()
    status_code = badRequestError.get("code")
    detail = badRequestError.get("message")
    default_code = badRequestError.get("name")

    def __init__(self, message=None):
        if message:
            self.detail = message

    def __str__(self):
        str(self.detail)