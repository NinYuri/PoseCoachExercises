import jwt
from django.conf import settings
from rest_framework import permissions

class IsAuthenticated(permissions.BasePermission):
    """
    Permite acceso a cualquier usuario autenticado (con token JWT válido) para cualquier metodo.
    """

    def has_permission(self, request, view):
        token = self._get_token_from_request(request)
        if not token:
            return False

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_is_active = payload.get('is_active', True)
            return user_is_active
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False

    def _get_token_from_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None