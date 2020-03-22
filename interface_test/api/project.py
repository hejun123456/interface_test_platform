from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from interface_test.models import Project, Debugtalk
from interface_test.serializer import ProjectSerializer
from interface_test.permission import IsAdmin

from django.db import transaction

import logging

logger = logging.getLogger(__name__)


class ProjectView(generics.ListCreateAPIView):
    """
    环境信息创建和全部查询
    项目创建时连带创建debugtalk条目
    """
    queryset = Project.objects.all().order_by('-create_time')
    serializer_class = ProjectSerializer

    def get(self, request, *args, **kwargs):
        """
        因为已经启用了分页，如果不写page参数，默认会返回page=1的结果，所以一定要带page参数来控制
        如果接口参数page=None，则返回全部数据，如果为正整数，返回对应页数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        logger.info("项目列表查询参数: {}".format(request.query_params))
        page = request.query_params.get('page')
        if page == 'None':
            self.pagination_class = None

        result = super().get(request, *args, **kwargs)
        # page = None时 , data是项目实例的字典列表;  page 非 None时, data是分页类的字典, data['results']为项目实例的字典列表
        p_list = result.data if page == 'None' else result.data['results']
        # 增加项目所属用例数和模块数
        for p in p_list:
            obj = Project.objects.get(pk=p['id'])
            p['testcase_count'] = obj.testcase.count()
            p['module_count'] = obj.module.count()

        return result

    def create(self, request, *args, **kwargs):
        """
        创建项目，连带创建debugtalk，创建失败则回滚
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = ProjectSerializer(data=request.data)
        error_msg = '项目创建失败, 原因：{}'

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # transaction.atomic实现事务回滚
                    project_obj = serializer.save()
                    # 创建debugtalk
                    Debugtalk.objects.create(project=project_obj)

                    logger.info('项目创建成功: {}'.format(serializer.data))
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(error_msg.format(e))
                return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # 前端检查字段长度，所以这里只检查到项目同名的问题
            logger.error(error_msg.format(serializer.errors))
            return Response({'message': '创建失败,已有同名项目', 'details': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    项目信息单查询、修改、和删除
    权限管理：
    1、删除需要管理权限，其他方法不需要。
    2、先对整个视图做管理权限限制
    3、再针对不同请求方法调整权限
    """
    queryset = Project.objects.all().order_by('-create_time')
    serializer_class = ProjectSerializer

    permission_classes = (IsAdmin,)  # 设置管理员权限

    def get_permissions(self):
        control_list = ('DELETE',)
        if self.request.method in control_list:
            # detele限制，需要管理员权限
            return super().get_permissions()
        # 清空权限限制
        return []
