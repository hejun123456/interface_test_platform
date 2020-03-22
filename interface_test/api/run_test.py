import os
import time

from djcelery.models import PeriodicTask
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from AutoTest import settings
from interface_test.common.runner import prepare_case, run_case, load_testcase
from interface_test.tasks import async_run, periodic_run
from interface_test.common.common import timestamp_to_datetime, bytes2str, tidy_tree_data, check_testcase_isRecursion

import logging

logger = logging.getLogger(__name__)


class DebugView(APIView):
    """
    用例调试视图,直接返回测试结果数据
    请求要求的参数:
    case_list: 如果是单独运行用例,value为case_id列表;如果是按模块或项目运行,value为{'module':module_id} / {'project':project_id}
    env: 环境id
    """
    def post(self, request):
        # 在request.data中获取
        task_info = request.data
        logger.info('用例调试数据：{}'.format(task_info))

        # 获取引用用例列表
        refs_list = []
        refs_list.extend(eval(task_info['before']))
        refs_list.extend(eval(task_info['after']))

        logger.info('当前用例的引用列表：{}'.format(refs_list))
        # 检查当前用例的引用是否有循环引用, 新增页调试时无id传入,取为None
        if check_testcase_isRecursion(task_info.get('id'), refs_list):
            return Response({'message': '用例循环引用'}, status=status.HTTP_400_BAD_REQUEST)

        # 用例运行路径
        test_root_path = os.path.join(settings.BASE_DIR, 'suite', 'debug_{}'.format(time.time()))
        test_project_path = os.path.join(test_root_path, str(task_info.get('project')))

        # 加载用例
        load_testcase(task_info, test_project_path=test_project_path, base_url=task_info.get('base_url'))

        # 运行用例
        summary = run_case(test_root_path)
        summary = timestamp_to_datetime(summary, type=False)
        # 原内容为字节类型不能序列化,需要转换。转换后作为响应返回前端
        summary = bytes2str(summary)
        # 返回用例中全部请求的结果树数据
        tree = []
        case_metas = [] # 保存用例的元数据,包括运行是否成功,断言结果等
        for record in summary['details'][0]['records']:
            # 调试结果树增加请求信息
            result = [
                {
                    'title': '请求(仅展示,匆提取)',
                    'expand': True,
                    'children': tidy_tree_data(record['meta_data']['request'], [])
                },
                {
                    'title': '响应',
                    'expand': True,
                    'children': tidy_tree_data(record['meta_data']['response'], [])
                }
            ]
            # one_record = tidy_tree_data(record['meta_data']['response'], [])
            # one_request = tidy_tree_data(record['meta_data']['request'], [])
            # 当前请求是否成功的标志、traceback（attachment）、validators
            case_run_info = {}
            case_run_info['flag'] = record['status'] == 'success'
            case_run_info['attachment'] = record['attachment']
            case_run_info['validators'] = record['meta_data']['validators']
            case_run_info['name'] = record['name']
            # 此为附加信息,页面展示时要先取出该数据
            case_metas.append(case_run_info)
            tree.append(result)

        return_info = {
            'tree': tree,
            'case_metas': case_metas,
            'summary': summary
        }

        # 返回结果
        return Response(return_info)


class TestView(APIView):
    """
    异步执行用例,生成测试报告,并返回测试报告路径,由前端跳转
    请求要求的参数:
    case_list: ,value为{'module':[module_id_list]} / {'project':[project_id_list]} / {‘case': [case_id_list]}
    env: 环境id
    """
    def post(self, request):
        # 在request.data中获取
        task_info = request.data
        logger.info('用例运行请求数据：{}'.format(task_info))
        # 用例运行路径
        test_root_path = os.path.join(settings.BASE_DIR, 'suite', 'test_{}'.format(time.time()))
        logger.info('用例路径：{}'.format(test_root_path))
        try:
            # 获取前端传入的报告名
            case_sum = prepare_case(task_info, test_root_path)
            # 如无可运行用例,返回错误
            if not case_sum:
                return Response({'message': '无可运行用例,请重新选择'}, status=status.HTTP_400_BAD_REQUEST)
            if task_info['case_list'].get('case') and task_info.get('runType') == 'sync':
                # 在用例列表选择用例时，runType==sync为同步，async则异步运行。
                # 项目和模块运行时，不进入此分支，只能异步运行
                summary = run_case(test_root_path)
                summary = timestamp_to_datetime(summary, type=False)
                return Response({'summary': summary})
            # 如果非case的，异步运行
            result = async_run.delay(test_root_path, task_info, case_sum)
            return Response({'message': '用例运行中,请稍后查询报告...', 'task_id': result.task_id})  # 返回task_id给调用者
        except KeyError as e:
            resp = {'message': 'missing key : {}'.format(e.args)}
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        except RecursionError:
            return Response({'message': '运行失败,用例存在循环引用情况,请检查'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'detail': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RunPeriodicTask(APIView):
    def post(self, request):
        # 任务记录的id
        task_id = request.data.get('task_id')
        logger.info('待运行任务id:{}'.format(task_id))
        try:
            # args列表，第一个元素为task_info
            args = eval(PeriodicTask.objects.get(pk=task_id).args)
            periodic_run.delay(*args)
            return Response({'message': '任务开始运行，请稍后查询结果...'})
        except PeriodicTask.DoesNotExist:
            resp = {
                'message': '所运行任务不存在，id:{}'.format(task_id)
            }
            return Response(resp)
