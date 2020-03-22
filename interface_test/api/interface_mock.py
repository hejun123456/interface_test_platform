import logging

from rest_framework import generics, status
from rest_framework.response import Response

from interface_test.models import InterfaceMock
from interface_test.serializer import InterfaceMockSerializer
from interface_test.common.mock_operator import interface_start, interface_stop

from interface_test.filtersets import InterfaceMockFilter
from interface_test.common.common import common_post, common_put

logger = logging.getLogger(__name__)


class InterfaceMockView(generics.ListCreateAPIView):
    """
    全局变量的增加和全部查询
    """
    queryset = InterfaceMock.objects.all().order_by('-create_time')
    serializer_class = InterfaceMockSerializer
    filterset_class = InterfaceMockFilter

    def post(self, request, *args, **kwargs):
        logger.info('接口创建数据：{}'.format(request.data))
        return common_post(self, request, error_msg='有同名接口,创建失败', *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        因为已经启用了分页，如果不写page参数，默认会返回page=1的结果，所以一定要带page参数来控制
        如果接口参数page=None，则返回全部数据，如果为正整数，返回对应页数据
        查询每个接口所属的场景数
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        page = request.query_params.get('page')
        if page == 'None':
            self.pagination_class = None

        result = super().get(request, *args, **kwargs)
        # page = None时 , data是模块实例的字典列表;  page 非 None时, data是分页类的字典, data['results']为模块实例的字典列表
        i_list = result.data if page == 'None' else result.data['results']
        # 增加项目所属用例数和模块数
        for i in i_list:
        # 增加模块所属用例数
            i['scene_count'] = InterfaceMock.objects.get(pk=i['id']).scene.count()

        return result


class InterfaceMockDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    全局变更 单查询、修改、和删除
    put 不修改接口状态
    patch 专门为修改接口状态
    """
    queryset = InterfaceMock.objects.all().order_by('-create_time')
    serializer_class = InterfaceMockSerializer

    def patch(self, request, *args, **kwargs):
        interface_id = kwargs.get('pk')
        isEnabled = request.data.get('enabled')
        interface_obj = self.queryset.filter(id=interface_id).first()
        resp = {}

        if interface_obj:
            # 启用
            try:
                if isEnabled:
                    interface_start(self.serializer_class(interface_obj).data)
                else:
                    interface_stop(interface_id)
                resp['message'] = '接口{}成功'.format('启用' if isEnabled else '禁用')
                logger.info('{},接口名：{}'.format(resp['message'], interface_obj.name))
                # 保存状态
                interface_obj.enabled = isEnabled
                interface_obj.save()
                return Response(resp)
            except Exception as e:
                resp['message'] = '接口{}失败,联系管理员'.format('启用' if isEnabled else '禁用')
                logger.error('{},接口名：{}\n报错：{}'.format(resp['message'], interface_obj.name, e))
                return Response(resp, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            resp['message'] = '数据不存在,id:{}'.format(interface_id)
            logger.error(resp['message'])
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        接口删除前要删除接口文件和settings数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        interface_id = kwargs.get('pk')
        interface_stop(interface_id)
        return super().delete(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        logger.info('接口修改数据：{}'.format(request.data))
        return common_put(self, request, error_msg='有同名接口,修改失败', *args, **kwargs)