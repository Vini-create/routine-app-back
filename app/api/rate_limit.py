from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter_kwargs = {"key_func": get_remote_address}

if settings.rate_limit_storage_uri_value:
    limiter_kwargs["storage_uri"] = settings.rate_limit_storage_uri_value

limiter = Limiter(**limiter_kwargs)
