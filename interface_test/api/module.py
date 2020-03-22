from rest_framework import generics

from interface_test.models import Module
from interface_test.serializer import ModuleSerializer
from interface_test.filtersets import ModuleFilter
from interface_test.common.common import common_put, common_post

import logging


logger = logging.getLogger(__name__)


class ModuleView(generics.ListCreateAPIView):
    """
    模块的列表查询和创建
    """
    queryset = Module.objects.all().order_by('-create_time')
    serializer_class = ModuleSerializer
    filterset_class = ModuleFilter

    def get(self, request, *args, **kwargs):
        """
        因为已经启用了分页，如果不写page参数，默认会返回page=1的结果，所以一定要带page参数来控制
        如果接口参数page=None，则返回全部数据，如果为正整数，返回对应页数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        logger.info('模块查询参数：{}'.format(request.query_params))
        page = request.query_params.get('page')
        if page == 'None':
            self.pagination_class = None

        result = super().get(request, *args, **kwargs)
        # page = None时 , data是模块实例的字典列表;  page 非 None时, data是分页类的字典, data['results']为模块实例的字典列表
        m_list = result.data if page == 'None' else result.data['results']
        # 增加项目所属用例数和模块数
        for m in m_list:
        # 增加模块所属用例数
            m['testcase_count'] = Module.objects.get(pk=m['id']).testcase.count()

        return result

    def post(self, request, *args, **kwargs):
        return common_post(self, request, error_msg='项目下有同名模块,创建失败', *args, **kwargs)


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    模块的查询、修改和删除
    """
    queryset = Module.objects.all().order_by('-create_time')
    serializer_class = ModuleSerializer

    def put(self, request, *args, **kwargs):
        return common_put(self, request, error_msg='项目下有同名模块,修改失败', *args, **kwargs)
