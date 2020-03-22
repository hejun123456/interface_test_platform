from rest_framework import generics, status
from rest_framework.response import Response

from interface_test.models import Report
from interface_test.serializer import ReportSerializer
from interface_test.permission import IsAdmin

import logging


logger = logging.getLogger(__name__)


class ReportView(generics.ListCreateAPIView):
    """
    报告信息增加和全部查询
    """
    queryset = Report.objects.filter(status=True).order_by('-create_time')
    serializer_class = ReportSerializer

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


class ReportDestroyView(generics.DestroyAPIView):
    """
    只提供报告删除功能，需要管理员权限
    权限管理：
    1、删除需要管理权限，其他方法不需要。
    2、先对整个视图做管理权限限制
    3、再针对不同请求方法调整权限
    """
    queryset = Report.objects.all().order_by('-create_time')
    serializer_class = ReportSerializer

    permission_classes = (IsAdmin,)  # 设置管理员权限

    def get_permissions(self):
        control_list = ('DELETE',)
        if self.request.method in control_list:
            # detele限制，需要管理员权限
            return super().get_permissions()
        # 清空权限限制
        return []

    def delete(self, request, *args, **kwargs):
        report_id = kwargs.get('pk')
        report_obj = Report.objects.get(pk=report_id)
        report_obj.status = False
        report_obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)