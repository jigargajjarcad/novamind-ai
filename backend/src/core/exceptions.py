class AppException(Exception):
    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(self, message: str | None = None, details: dict | None = None):
        super().__init__(message or self.code)
        self.details: dict = details or {}


class NotFoundError(AppException):
    code = "NOT_FOUND"
    status_code = 404


class UnauthorizedError(AppException):
    code = "UNAUTHORIZED"
    status_code = 401


class ForbiddenError(AppException):
    code = "FORBIDDEN"
    status_code = 403


class ConflictError(AppException):
    code = "CONFLICT"
    status_code = 409


class FileTooLargeError(AppException):
    code = "FILE_TOO_LARGE"
    status_code = 413


class InvalidFileTypeError(AppException):
    code = "INVALID_FILE_TYPE"
    status_code = 415


class UserNotFoundError(NotFoundError):
    code = "USER_NOT_FOUND"


class EmailAlreadyExistsError(ConflictError):
    code = "EMAIL_ALREADY_EXISTS"


class InvalidCredentialsError(UnauthorizedError):
    code = "INVALID_CREDENTIALS"


class CollectionNotFoundError(NotFoundError):
    code = "COLLECTION_NOT_FOUND"


class DocumentNotFoundError(NotFoundError):
    code = "DOCUMENT_NOT_FOUND"


class DocumentProcessingError(AppException):
    code = "DOCUMENT_PROCESSING_ERROR"
    status_code = 422


class ChatSessionNotFoundError(NotFoundError):
    code = "CHAT_SESSION_NOT_FOUND"


class EmailNotVerifiedError(ForbiddenError):
    code = "EMAIL_NOT_VERIFIED"


class AdminRequiredError(ForbiddenError):
    code = "ADMIN_REQUIRED"


class InvalidPasswordError(AppException):
    code = "INVALID_PASSWORD"
    status_code = 400


class TokenInvalidError(AppException):
    code = "TOKEN_INVALID"
    status_code = 400


class TokenExpiredError(AppException):
    code = "TOKEN_EXPIRED"
    status_code = 400


class RateLimitError(AppException):
    code = "RATE_LIMITED"
    status_code = 429
