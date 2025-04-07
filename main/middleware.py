from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from oauth2_provider.models import AccessToken
from django.utils.timezone import now
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@database_sync_to_async
def get_user_from_oauth2_token(token_key):
    try:
        # Validate the token and check if it's still valid
        access_token = AccessToken.objects.get(
            token=token_key, expires__gt=now())
        return access_token.user
    except AccessToken.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        query_params = {}

        # Parse query string safely
        if query_string:
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value

        token_key = query_params.get('token', None)
        if token_key:
            logger.info(f"OAuth2 Token received: {token_key}")
            scope['user'] = await get_user_from_oauth2_token(token_key)
            if isinstance(scope['user'], AnonymousUser):
                logger.warning("Invalid OAuth2 token provided")
        else:
            scope['user'] = AnonymousUser()
            logger.warning("No token provided")

        return await super().__call__(scope, receive, send)
