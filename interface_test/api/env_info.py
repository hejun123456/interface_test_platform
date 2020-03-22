from rest_framework import generics

from interface_test.models import EnvInfo
from interface_test.serializer import EnvInfoSerializer
from interface_test.permission import IsAdmin
from interface_test.common.common import common_put, common_post

import logging


logger = logging.getLogger(__name__)


class EnvInfoView(generics.ListCreateAPIView):
    """
    环境信息增加和全部查询
    """
    queryset = EnvInfo.objects.all().order_by('-create_time')
    serializer_class = EnvInfoSerializer

    def get(self, request, *args, **kwargs):
        """
        因为已经启用了分页，如果不写page参数，默认会返回page=1的结果，所以一定要带page参数来控制
        如果接口参数page=None，则返回全部数据，如果为正整数，返回对应页数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if request.query_params.get('page') == 'None':
            self.pagination_class = None

        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return common_post(self, request, error_msg='有同名或同地址的环境,创建失败', *args, **kwargs)


class EnvInfoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    环境信息单查询、修改、和删除
    权限管理：
    1、删除需要管理权限，其他方法不需要。
    2、先对整个视图做管理权限限制
    3、再针对不同请求方法调整权限
    """
    queryset = EnvInfo.objects.all().order_by('-create_time')
    serializer_class = EnvInfoSerializer

    permission_classes = (IsAdmin,)  # 设置管理员权限

    def get_permissions(self):
        control_list = ('DELETE',)
        if self.request.method in control_list:
            # detele限制，需要管理员权限
            return super().get_permissions()
        # 清空权限限制
        return []

    def put(self, request, *args, **kwargs):
        return common_put(self, request, error_msg='有同名或同地址的环境,修改失败', *args, **kwargs)