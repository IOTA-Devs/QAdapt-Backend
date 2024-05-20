from enum import Enum

class ErrorCodes(Enum):
    GENERAL_ERROR = 1000 # A generic error indicating that something went wrong and no specific error code is available
    INVALID_REQUEST = 1100 # The request is invalid and cannot be processed
    INVALID_JSON = 1101 # The JSON payload is invalid
    INVALID_PARAMETER = 1102 # A parameter in the request is invalid
    FILE_TOO_LARGE = 1103 # The file is too large
    RESOURCE_NOT_FOUND = 1104 # The requested resource was not found
    PROCESSING_ERROR = 1105 # An error occurred while processing the request
    VALIDATION_ERROR = 1200 # An error occurred while validating the request
    RESOURCE_CONFLICT = 1300 # A conflict occurred while processing the request
    RATE_LIMIT_EXCEEDED = 1400 # The rate limit for the request has been exceeded
    SERVICE_UNAVAILABLE = 1500 # The service is currently unavailable
    INTERNAL_SERVER_ERROR = 1501 # An internal server error occurred
    AUTHENTICATION_ERROR = 1600 # An error occurred while authenticating the request
    INCORRECT_CREDENTIALS = 1601 # The credentials provided are incorrect