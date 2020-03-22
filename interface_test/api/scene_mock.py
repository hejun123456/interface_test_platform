import logging

from rest_framework import generics, status
from rest_framework.response import Response

from interface_test.models import SceneMock
from interface_test.serializer import SceneMockSerializer
from interface_test.common.mock_operator import scene_start, scene_stop

from interface_test.filtersets import SceneMockFilter
from interface_test.common.common import common_post, common_put

logger = logging.getLogger(__name__)


class SceneMockView(generics.ListCreateAPIView):
    """
    全局变量的增加和全部查询
    """
    queryset = SceneMock.objects.all().order_by('-create_time')
    serializer_class = SceneMockSerializer
    filterset_class = SceneMockFilter

    def post(self, request, *args, **kwargs):
        logger.info('接口创建数据：{}'.format(request.data))
        return common_post(self, request, error_msg='有同名场景,创建失败', *args, **kwargs)


class SceneMockDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    全局变更 单查询、修改、和删除
    """
    queryset = SceneMock.objects.all().order_by('-create_time')
    serializer_class = SceneMockSerializer

    def patch(self, request, *args, **kwargs):
        scene_id = kwargs.get('pk')
        isEnabled = request.data.get('enabled')
        scene_obj = self.queryset.filter(id=scene_id).first()
        resp = {}

        if scene_obj:
            # 启用
            try:
                action = scene_start if isEnabled else scene_stop
                action(self.serializer_class(scene_obj).data)
                resp['message'] = '场景{}成功'.format('启用' if isEnabled else '禁用')
                logger.info('{},场景名：{}'.format(resp['message'], scene_obj.name))
                # 保存状态
                scene_obj.enabled = isEnabled
                scene_obj.save()
                return Response(resp)
            except Exception as e:
                resp['message'] = '场景{}失败,联系管理员'.format('启用' if isEnabled else '禁用')
                logger.error('{},场景名：{}\n报错：{}'.format(resp['message'], scene_obj.name, e))
                return Response(resp, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            resp['message'] = '数据不存在,id:{}'.format(scene_id)
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
        scene_id = kwargs.get('pk')
        scene_obj = self.queryset.filter(id=scene_id).first()
        scene_stop(self.serializer_class(scene_obj).data)
        return super().delete(self, request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        logger.info('接口修改数据：{}'.format(request.data))
        return common_put(self, request, error_msg='有同名场景,修改失败', *args, **kwargs)