from __future__ import absolute_import

import os
import time

from celery import shared_task
from django.conf import settings

from interface_test.common.runner import run_case, prepare_case
from interface_test.models import Report, EnvInfo
from interface_test.common.common import timestamp_to_datetime, testcase_summary, top10error
from interface_test.common.emails import send_email


def run_task(func, test_root_path, task_info, case_sum, gen_report=False, report_name=None):
    """
    主要是抽离任务运行逻辑
    :param test_root_path:
    :param task_info:
    :param case_sum:
    :param gen_report:
    :param report_name:
    :return:
    """
    # 保存报告名和任务id关联
    report_obj = Report.objects.create(
        report_name=task_info.get('report_name') + ' ' + time.strftime("%Y%m%d-%H%M%S", time.localtime()),
        task_id=func.request.id, description=task_info.get('description'), case_sum=case_sum)
    # 运行用例
    summary = run_case(test_root_path, gen_report=gen_report, report_name=report_name)
    summary = timestamp_to_datetime(summary, type=False)
    # 增加环境信息
    env_obj = EnvInfo.objects.get(pk=task_info['env'])
    summary['base_url'] = '{}({})'.format(env_obj.env_name, env_obj.base_url)
    # 添加top10错误表数据及其他统计数据
    summary['top10error'], summary['successes'], summary['failures'], summary['errors'] = top10error(summary)
    # 修改任务数据
    report_obj.result = 'Pass' if summary['success'] else 'Fail'
    report_obj.duration = round(summary['time']['duration'], 2)
    report_obj.start_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(summary['time']['start_at']))
    # 统计用例情况
    report_obj.case_pass, report_obj.case_failure, report_obj.case_error, report_obj.skipped = testcase_summary(summary)

    if func.__name__ == 'periodic_run':
        # 发送邮件
        receivers = task_info.get('receivers')  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        if len(receivers) > 0:
            # 收件人不为空，才发邮件
            send_email(task_info.get('report_name'), summary, receivers)

    report_obj.save() # 发送邮件比较耗时，发送才更新页面上的结果

    return summary


@shared_task
def async_run(test_root_path, task_info, case_sum, gen_report=False, report_name=None):
    return run_task(async_run, test_root_path, task_info, case_sum, gen_report=gen_report, report_name=report_name)


@shared_task
def periodic_run(task_info):
    """
    task_info = {
        case_list: {
          case: caseList
        },
        env: this.base_url,
        report_name: this.reportName.trim() + ' ' + new Date().toLocaleString(),
        description: this.reportDescription
      }
    :param task_info:
    :return:
    """
    # 用例运行路径
    test_root_path = os.path.join(settings.BASE_DIR, 'suite', 'test_{}'.format(time.time()))

    try:
        # 获取前端传入的报告名
        case_sum = prepare_case(task_info, test_root_path)
        # 如无可运行用例,返回错误
        if not case_sum:
            return {'message': '无可运行用例,请重新选择'}
        # 运行并返回用例结果
        return run_task(periodic_run, test_root_path, task_info, case_sum, gen_report=False, report_name=None)
    except KeyError as e:
        resp = {'message': 'missing key : {}'.format(e.args)}
        return resp
    except RecursionError:
        return{
            'message': '运行失败,用例存在循环引用情况,请检查',
        }