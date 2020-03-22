from rest_framework import generics

from interface_test.models import GlobalVar
from interface_test.serializer import GlobalVarSerializer
from interface_test.filtersets import GlobalVarFilter
import logging

from interface_test.common.common import common_put, common_post

logger = logging.getLogger(__name__)


class GlobalVarView(generics.ListCreateAPIView):
    """
    全局变量的增加和全部查询
    """
    queryset = GlobalVar.objects.all().order_by('-create_time')
    serializer_class = GlobalVarSerializer
    filterset_class = GlobalVarFilter

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
    
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return common_post(self, request, error_msg='有同名变量,创建失败', *args, **kwargs)


class GlobalVarDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    全局变更 单查询、修改、和删除
    """
    queryset = GlobalVar.objects.all().order_by('-create_time')
    serializer_class = GlobalVarSerializer

    def put(self, request, *args, **kwargs):
        return common_put(self, request, error_msg='有同名变量,修改失败', *args, **kwargs)
