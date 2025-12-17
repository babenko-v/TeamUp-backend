class ApplicationException(Exception):
    def __init__(self, message: str = "An application error occurred"):
        self.message = message
        super().__init__(self.message)

class NotFoundException(ApplicationException):
    pass

class AccessDeniedException(ApplicationException):

    pass

class ValidationException(ApplicationException):
    pass

class AlreadyExistsException(ApplicationException):
    pass