class AuthServiceError(Exception):
    """Базовая ошибка сервиса аутентификации."""


class EmailAlreadyRegisteredError(AuthServiceError):
    """Возникает при попытке зарегистрировать уже существующий email."""


class InvalidCredentialsError(AuthServiceError):
    """Возникает при передаче неверных учётных данных."""

class InvalidUserDataError(AuthServiceError):
    """Возникает при передаче некорректных данных пользователя."""


class UserInactiveError(AuthServiceError):
    """Возникает при попытке аутентификации неактивного пользователя."""


class UserNotFoundError(AuthServiceError):
    """Возникает, если пользователь не найден."""

class TokenNotFoundError(AuthServiceError):
    """Возникает, если токен отсутствует."""

class InvalidTokenError(AuthServiceError):
    """Возникает, если токен недействителен или не может быть проверен."""


class TokenExpiredError(AuthServiceError):
    """Возникает при попытке использовать истёкший токен."""


class TokenRevokedError(AuthServiceError):
    """Возникает при попытке использовать отозванный токен."""


class InvalidTokenTypeError(AuthServiceError):
    """Возникает, если токен имеет неподходящий тип."""

class TokenAlreadyRevokedError(AuthServiceError):
    """Возникает при попытке повторно отозвать токен."""