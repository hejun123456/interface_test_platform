from rest_framework import generics

from interface_test.models import Debugtalk
from interface_test.serializer import DebugTalkSerializer
from interface_test.permission import IsAdmin

import logging


logger = logging.getLogger(__name__)


class DebugtalkView(generics.ListAPIView):
    """
    只提供查询，不提供创建，由项目创建时连带创建
    debugtalk全部查询
    """
    queryset = Debugtalk.objects.all().order_by('-create_time')
    serializer_class = DebugTalkSerializer


class DebugtalkDetailView(generics.RetrieveUpdateAPIView):
    """
    debugtalk信息单查询、修改
    不提供删除方法，删除项目时级联删除
    """
    queryset = Debugtalk.objects.all().order_by('-create_time')
    serializer_class = DebugTalkSerializer
