class DomainException(Exception):
    """Base exception for all domain-level errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class NotFoundException(DomainException):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(status_code=404, message=message)


class ForbiddenException(DomainException):
    """Raised when the caller lacks permission for the action."""

    def __init__(self, message: str = "Action not allowed"):
        super().__init__(status_code=403, message=message)


class BadRequestException(DomainException):
    """Raised when input data is invalid or incomplete."""

    def __init__(self, message: str = "Bad request"):
        super().__init__(status_code=400, message=message)


class ConflictException(DomainException):
    """Raised when the action conflicts with current resource state (duplicate, wrong status, etc.)."""

    def __init__(self, message: str = "Conflict"):
        super().__init__(status_code=409, message=message)


class InternalLogicException(DomainException):
    """Raised on unexpected server-side logic errors."""

    def __init__(self, message: str = "Internal error"):
        super().__init__(status_code=500, message=message)

