import json
import logging

from rest_framework import generics, status

from djcelery.models import PeriodicTask, CrontabSchedule, PeriodicTasks
from rest_framework.response import Response

from interface_test.models import TaskExtend, User
from interface_test.serializer import PeriodicTaskSerializer, TaskExtendSerializer
from interface_test.permission import IsAdmin
from interface_test.filtersets import PeriodicTaskFilter

logger = logging.getLogger(__name__)

class PeriodicTaskView(generics.ListCreateAPIView):
    """
    提供查询，创建
    """
    queryset = PeriodicTask.objects.all().order_by('-date_changed')
    serializer_class = PeriodicTaskSerializer
    filterset_class = PeriodicTaskFilter

    def post(self, request, *args, **kwargs):
        """
        1、先创建或获取Crontab实例
        2、保存任务实例
        data 不要带日期类数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # QueryDict无法修改，所以通过下面方式复制数据，再修改
        data = json.loads(json.dumps(request.data))
        logger.info('创建任务请求数据：{}'.format(data))
        # 获取或创建crontab
        # crontab_time = {
        #     'minute': '1',
        #     'hour':'1',
        #     'day_of_week':'*',
        #     'day_of_month':'*',
        #     'month_of_year':'*'
        # }
        project = int(data.pop('project'))
        crontab_time = data.get('crontab')
        if crontab_time:
            # 如果不带crontab的任务,则是手动运行的
            crontab, _ = CrontabSchedule.objects.get_or_create(**crontab_time)
            data['crontab'] = crontab.id
        data['task'] = 'interface_test.tasks.periodic_run' # 后期可改为动态获取
        # 保存任务实例
        email_list = data.pop('email_list')
        author = data.pop('author')
        serializer = PeriodicTaskSerializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save()
                obj = PeriodicTask.objects.get(pk=serializer.data['id'])
                PeriodicTasks.changed(obj) # 必须执行此更新,触发celery beat刷新
                # 保存拓展信息
                TaskExtend.objects.create(**{
                    'email_list': email_list,
                    'author': author,
                    'periodic_task_id': serializer.data['id'],
                    'project': project
                })
                logger.info('任务添加成功： {}'.format(serializer.data))
                return Response(serializer.data)
            except Exception as e:
                logger.error('任务创建失败,原因：{}'.format(e))
                return Response({'detail': serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(serializer.errors)
            return Response({'message': '创建失败,已有同名任务', 'detail': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class PeriodicTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    debugtalk信息单查询、修改、删除
    """
    queryset = PeriodicTask.objects.all().order_by('-date_changed')
    serializer_class = PeriodicTaskSerializer

    def put(self, request, *args, **kwargs):
        # QueryDict无法修改，所以通过下面方式复制数据，再修改
        data = json.loads(json.dumps(request.data))
        # 获取或创建crontab
        project = int(data.pop('project'))
        crontab_time = data.get('crontab')
        if crontab_time:
            # 如果不带crontab的任务,则是手动运行的
            crontab, _ = CrontabSchedule.objects.get_or_create(**crontab_time)
            data['crontab'] = crontab.id
        # 保存任务实例
        task_extend = data.pop('task_extend')
        task_extend['project'] = project # 更新所属项目
        task_extend['email_list'] = data.pop('email_list')
        logger.info('修改任务请求数据：{}'.format(data))
        logger.info('修改任务拓展请求数据：{}'.format(task_extend))
        try:
            PeriodicTask.objects.filter(pk=data['id']).update(**data)
            obj = PeriodicTask.objects.get(pk=data['id'])
            PeriodicTasks.changed(obj) # 必须执行此更新,触发celery beat刷新
            # 保存拓展信息
            TaskExtend.objects.filter(pk=task_extend.get('id')).update(**task_extend)
            return Response({'message': '任务修改成功'})
        except Exception as e:
            logger.error('任务修改失败,原因：{}'.format(e))
            return Response({'message': '修改失败,已有同名任务'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(elf, request, *args, **kwargs):
        try:
            obj = PeriodicTask.objects.get(pk=kwargs.get('pk'))
            obj.enabled = request.data.get('enabled')
            obj.save()
            PeriodicTasks.changed(obj) # 必须执行此更新,触发celery beat刷新
            return Response({'message': '{}成功'.format('启用' if obj.enabled else '禁用')})
        except Exception as e:
            logger.error('任务修改失败,原因：{}'.format(e))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)