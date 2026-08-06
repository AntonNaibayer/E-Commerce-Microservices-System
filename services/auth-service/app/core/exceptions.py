class InvalidTokenTypeError(Exception):
    """Тип токена не совпадает с ожидаемым (например, refresh вместо access)."""