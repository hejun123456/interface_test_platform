# 使用APIView
import json
from celery.result import AsyncResult
# Create your views here.
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import re
import os

from interface_test.common.common import get_refs_link
from .models import Debugtalk, Project, TestCase, Module, Report
from django.conf import settings
import datetime
from django.db.models import Sum

import logging


logger = logging.getLogger(__name__)


@api_view(['POST'])
def check_result(request):
    """
    通过任务id查询任务结果
    :param request:
    :param task_id:
    :return:
    """
    task_id = request.data.get('task_id')
    if task_id is None:
        return Response({'message': '缺少task_id'}, status=status.HTTP_400_BAD_REQUEST)

    res = AsyncResult(task_id)
    if res.ready(): # 检查指定任务是否已经完成
        if res.successful():
            return Response(res.result) # res.result为任务函数的返回值，即任务结果
        return Response({'message': '任务运行错误：{}'.format(res.result)})
    return Response({'message': '任务运行中，稍后查看...'})


@api_view(['GET'])
def get_all_func(request):
    """
    用于获取当前全部项目的debugtalk中的可用函数
    :return:
    """
    debugtalk = Debugtalk.objects.all()
    # 查找全部函数, def与括号之间，取函数名与括号
    findall_pattern = re.compile(r'def(.*?\(.*?\n*?.*?\))')
    # 查找全部被注释的函数
    findall_invalid_pattern = re.compile(r'#.*?def(.*?\(.*?\n*?.*?\))')
    # 结果容器  数据结构 {'project_name': [funcList], ...}
    funcs = {}

    # 读取公共函数名
    with open(os.path.join(settings.BASE_DIR, 'httprunner_extend_functions.py'), encoding='utf-8') as f:
        code = f.read()
        common_list = findall_pattern.findall(code)
        common_invalid_list = findall_invalid_pattern.findall(code)
        # common_valid_list = ['${' + func.strip().replace('\n', '') + '}' for func in list(set(common_list) - set(common_invalid_list))]
        common_valid_list = ['${' + re.sub(r'\n\s*', '', func.strip()) + '}' for func in list(set(common_list) - set(common_invalid_list))]
        funcs['common'] = common_valid_list

    # 读取自定义函数名
    for dbg in debugtalk:
        all_list = findall_pattern.findall(dbg.debugtalk)
        all_invalid_list = findall_invalid_pattern.findall(dbg.debugtalk)
        # 使用集合运算获取到可用函数列表  以及 函数名去空格,并适配httprunner的引用格式
        valid_list = ['${'+func.strip()+'}' for func in list(set(all_list) - set(all_invalid_list))]
        if valid_list:
            # 以所属项目名为key， 可用函数列表为value
            funcs[dbg.project.project_name] = valid_list

    return Response(funcs)


@api_view(['GET'])
def get_dashboard_info(request):
    days = datetime.timedelta(days=29) # 包括今天，近30天前的日期
    today = datetime.date.today()
    date30before = today - days

    # series图表数据
    series = {
        'date': [],
        'skipped': [0 for x in range(30)], # 平台未实现跳过用例，都是0
        'errors': [],
        'failures': [],
        'successes': []
    }
    for x in range(29, -1, -1):
        day = datetime.timedelta(days=x)
        target_date = today-day
        end = target_date + datetime.timedelta(days=1)
        # 日期列表
        series['date'].append(target_date.strftime('%Y-%m-%d'))
        # 成功用例统计
        # date_successes = Report.objects.filter(create_time__year=target_date.year,
        # create_time__month=target_date.month,
        # create_time__day=target_date.day).aggregate(Sum('case_pass'))['case_pass__sum']
        date_successes = Report.objects.filter(create_time__range=(target_date, end)).aggregate(Sum('case_pass'))['case_pass__sum']
        series['successes'].append(date_successes or 0)

        date_failures = Report.objects.filter(create_time__range=(target_date, end)).aggregate(Sum('case_failure'))['case_failure__sum']
        series['failures'].append(date_failures or 0)

        date_errors = Report.objects.filter(create_time__range=(target_date, end)).aggregate(Sum('case_error'))['case_error__sum']
        series['errors'].append(date_errors or 0)

    run_case = Report.objects.all().aggregate(Sum('case_sum'), Sum('case_pass'))
    run_case_sum, run_case_pass = run_case['case_sum__sum'], run_case['case_pass__sum']
    data = {
        'project_num': Project.objects.all().count(),
        'module_num': Module.objects.all().count(),
        'testcase_num': TestCase.objects.all().count(),
        'new_testcase_num': TestCase.objects.filter(create_time__gte=date30before).count(), #近30天新增用例数
        'run_case_sum': run_case_sum, #用例累计执行数 #用例累计执行成功数
        'run_case_pass': run_case_pass,
        'series': series
    }

    return Response(data)


@api_view(['GET'])
def getrefslink(request, tc_id):
    return Response(get_refs_link(int(tc_id), True))


@api_view(['POST'])
def getrefscase(request):
    row = TestCase.objects.get(pk=request.data.get('id'))
    logger.info(request.data)
    before_list = eval(row.before)
    before_list_new = []
    after_list = eval(row.after)
    after_list_new = []
    try:
        for before in before_list:
            obj = TestCase.objects.get(pk=before[0])
            before_list_new.append((obj.id, obj.name))
        for after in after_list:
            obj = TestCase.objects.get(pk=after[0])
            after_list_new.append((obj.id, obj.name))
        return Response({
            'before': json.dumps(before_list_new),
            'after': json.dumps(after_list_new)
        })
    except TestCase.DoesNotExist:
        return Response({'message': '引用用例已被删除'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def copy_testcase(request):
    data = request.data
    logger.info('复制用例信息：{}'.format(data))
    try:
        obj = TestCase.objects.get(pk=data.get('id'))
        obj.id = None
        obj.name = data.get('name')
        obj.author = request.user
        obj.save()
        return Response({'message': '用例复制成功'})
    except TestCase.DoesNotExist:
        return Response({'message': '复制用例不存在'}, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError:
        return Response({'message': '复制用例不能重名'}, status=status.HTTP_400_BAD_REQUEST)