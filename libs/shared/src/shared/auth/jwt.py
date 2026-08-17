import jwt
from pydantic import ValidationError

from .exceptions import InvalidTokenError
from .schemas import AccessTokenPayload


def decode_access_token(
    token: str,
    public_key: str,
    algorithm: str,
) -> AccessTokenPayload:
    try:
        payload = jwt.decode(
            jwt=token,
            key=public_key,
            algorithms=[algorithm],
        )

        if payload.get("token_type") != "access":
            raise InvalidTokenError()

        return AccessTokenPayload.model_validate(payload)

    except (jwt.InvalidTokenError, ValidationError) as e:
        raise InvalidTokenError() from e