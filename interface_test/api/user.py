from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from interface_test.models import User, Token
from interface_test.serializer import UserSerializer
from interface_test.permission import IsAdmin

import hashlib
import time

import logging


# 生成一个以当前文件名为名字的logger实例
logger = logging.getLogger(__name__)


class RegView(APIView):
    """
    用户注册
    """
    authentication_classes = ()
    def post(self, request):
        resp = {}
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # 使用接口只能创建普通用户
            # 管理员用户使用后台用户手工创建
            serializer.save()
            resp['message'] = '账号{}注册成功'.format(request.data.get('username'))
            resp['data'] = serializer.data
            logger.info(resp['message'])

            return Response(resp)
        else:
            if serializer.errors['username'][0].code == 'unique':
                resp['message'] = '账号{}已注册过'.format(request.data.get('username'))
            else:
                resp['message'] = '账号{}注册失败，联系管理员'.format(request.data.get('username'))
            logger.error('注册失败，原因：{}'.format(serializer.errors))
            logger.error('请求信息：{}'.format(request.data))

            return Response(resp, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    """
    获取用户信息（单个或全部）
    权限：管理员
    """
    # permission_classes = (IsAdmin,)
    def get(self, request, uid=None):
        if uid:
            try:
                user = User.objects.get(pk=uid)
                serializer = UserSerializer(user)
            except Exception:
                logger.error('uid: {}'.format(uid))
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            users = User.objects.all().order_by('-create_time')
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class LogintView(APIView):
    """
    登录视图
    登录入参：用户、密码
    """
    authentication_classes = ()

    def get_token(self, user):
        # 生成token串
        md5 = hashlib.md5()
        u_t = user.username + str(time.time())
        md5.update(u_t.encode())
        token_str = md5.hexdigest()
        token = Token.objects.filter(user=user).first()
        if token:
            # 重复登录，更新token和更新时间
            token.token = token_str
            token.save()
        else:
            token = Token.objects.create(user=user, token=token_str)
        return token

    def post(self, request):
        resp = {}
        try:
            username = request.data['username']
            password = request.data['password']
            user = User.objects.get(username=username, password=password)
            token = self.get_token(user)
        except KeyError as e:
            resp['message'] = '{}为必填'.format(e)
            logger.error('登录失败，原因：{}为必填'.format(e))
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            resp['message'] = '账号或密码错误'
            logger.info(resp['message'])
            return Response(resp, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(user)
        resp['authorization'] = token.token
        resp['user'] = serializer.data
        resp['message'] = '登录成功'
        logger.info('用户{}{}'.format(username, resp['message']))
        return Response(resp)


class LogoutView(APIView):
    """
    登出视图
    """
    authentication_classes = ()

    def post(self, request):
        resp = {}
        # token = request.META.get('Token', None)
        token = request._request.headers.get('authorization', None)
        username = request.data.get('username', None)
        if token is None or username is None:
            resp['message'] = '未带token或用户名'
            logger.error(resp['message'])
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                token = Token.objects.get(token=token, user__username=username)
                token.delete()
                resp['message'] = '登出成功'
                logger.info('用户{}登出成功'.format(username))
                return Response(resp)
            except Token.DoesNotExist:
                resp['message'] = 'token或账号无效,请重新登录'
                logger.error(resp['message'])
                return Response(resp, status=status.HTTP_401_UNAUTHORIZED)
