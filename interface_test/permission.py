from rest_framework import  permissions

from interface_test.models import Token


class IsAdmin(permissions.BasePermission):
    """
    权限校验
    """
    def has_permission(self, request, view):
        # user.role 为0或1
        token = request._request.headers.get('authorization')
        try:
            token_obj = Token.objects.get(token=token)
            user = token_obj.user
        except Token.DoesNotExist:
            return False
        return user.role