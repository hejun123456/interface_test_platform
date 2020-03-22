from rest_framework.authentication import BaseAuthentication
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import ugettext_lazy as _
import datetime
import pytz


# token有效时间，单位为小时
token_valid_time = 12

from interface_test.models import Token


class NewAuthenticationFailed(APIException):
    # 使用原来exceptions中定义的AuthenticationFailed，返回状态码是403， 不对。
    # 所以重新定义一下
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Incorrect authentication credentials.')
    default_code = 'authentication_failed'


def is_token_valid(token_obj):
    # upadte_time是datetime.datetime对象
    update_time = token_obj.update_time

    now = datetime.datetime.now()
    now = now.replace(tzinfo=pytz.timezone('UTC'))
    # 时间差
    timedelta = datetime.timedelta(hours=token_valid_time)

    if now - update_time > timedelta:
        token_obj.delete()
        raise NewAuthenticationFailed()


class AuthenticationView(BaseAuthentication):
    """
    认证类
    """
    def authenticate(self, request):
        token = request._request.headers.get('authorization', None)
        try:
            token_obj = Token.objects.get(token=token)
            is_token_valid(token_obj)
        except Token.DoesNotExist:
            raise NewAuthenticationFailed()
        return (token_obj.user, token_obj)

    def authenticate_header(self, request):
        pass