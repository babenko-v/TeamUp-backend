class BaseHandleException(Exception):
    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)

class NotFoundException(BaseHandleException):
    pass

class AccessDeniedException(BaseHandleException):
    pass

class ValidationException(BaseHandleException):
    pass

class AlreadyExistsException(BaseHandleException):
    pass
