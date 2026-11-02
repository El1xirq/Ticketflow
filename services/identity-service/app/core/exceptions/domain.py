from app.core.exceptions.base import AppException

class InvalidTokenException(AppException):
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(detail=detail, status_code=401, error_code="UNAUTHORIZED")


class DatabaseException(AppException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(detail=detail, status_code=500, error_code="DATABASE_ERROR")


class InvalidCredentialsException(AppException):
    def __init__(self, detail: str = "Invalid user credentials"):
        super().__init__(detail=detail, status_code=401, error_code="UNAUTHORIZED")


class NotFoundException(AppException):
    def __init__(self, detail: str = "Recource not found"):
        super().__init__(detail=detail, status_code=401, error_code="NOT_FOUND")


class ConflictException(AppException):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=409, error_code="CONFLICT")

class PermissionDeniedException(AppException):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=403, error_code="FORBIDDEN")