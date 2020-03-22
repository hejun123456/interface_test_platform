from rest_framework.response import Response
from rest_framework import generics, status

from interface_test.filtersets import TestCaseFilter
from interface_test.models import TestCase
from interface_test.serializer import TestCaseSerializer
from interface_test.common.common import common_post, common_put, check_testcase_isRecursion

import logging

logger = logging.getLogger(__name__)


class TestCaseView(generics.ListCreateAPIView):
    """
    模块的列表查询和创建
    """
    queryset = TestCase.objects.all().order_by('-create_time')
    serializer_class = TestCaseSerializer
    filterset_class = TestCaseFilter

    def get(self, request, *args, **kwargs):
        """
        因为已经启用了分页，如果不写page参数，默认会返回page=1的结果，所以一定要带page参数来控制
        如果接口参数page=None，则返回全部数据，如果为正整数，返回对应页数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        logger.info("testcase list query params: {}".format(request.query_params))
        if request.query_params.get('page') == 'None':
            self.pagination_class = None

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return common_post(self, request, error_msg='有同名用例,创建失败', *args, **kwargs)


class TestCaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    模块的查询、修改和删除
    """
    queryset = TestCase.objects.all().order_by('-create_time')
    serializer_class = TestCaseSerializer

    def put(self, request, *args, **kwargs):
        logger.info('用例修改信息：{}'.format(request.data))
        # 检查引用中是否有循环引用
        pk = kwargs.get('pk') # 用例id
        before = eval(request.data.get('before'))
        after = eval(request.data.get('after'))
        before.extend(after) # 合并内容

        # 检查当前用例的引用是否有循环引用
        if check_testcase_isRecursion(pk, before):
            return Response({'message': '用例循环引用'}, status=status.HTTP_400_BAD_REQUEST)

        return common_put(self, request, error_msg='有同名用例,修改失败', *args, **kwargs)
