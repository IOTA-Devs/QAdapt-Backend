from .ErrorCodes import ErrorCodes

class Error():
    def __init__(self, message: str, status_code: ErrorCodes):
        self.message = message
        self.status_code = status_code

    def to_json(self):
        return {
            'message': self.message,
            'code': self.status_code.value
        }