class InvalidTokenError(Exception):
    """Токен отсутствует, некорректен, истёк или имеет неверный тип"""

class ForbiddenError(Exception):
    """Недостаточно прав для выполнения операции"""