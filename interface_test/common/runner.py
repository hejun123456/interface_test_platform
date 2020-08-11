import shutil

from httprunner import HttpRunner
from rest_framework import status
from rest_framework.response import Response

from interface_test.common.file_operate import to_file, to_yaml_file
from interface_test.models import GlobalVar, Debugtalk, TestCase, ParamsFile, EnvInfo, Project, Module
import os
from django.conf import settings

import logging


logger = logging.getLogger(__name__)


def load_env():
    """
    加载全局的环境变量
    :param test_root_path:
    :return:
    """
    # 由原来加载环境变量文件改为把环境变量加载到config中
    vars_list = GlobalVar.objects.all().values('var_name', 'var_value')

    vars_dict_list = []

    for item in vars_list:
        try:
            value = eval(item['var_value'])
        except Exception:
            value = item['var_value']
        vars_dict_list.append({item['var_name']: value})

    return vars_dict_list


def load_debugtalk(test_project_path, project_id, base_url):
    """
    加载全局的debugtalk.py文件、环境变量 和 拓展的内置函数
    :param test_root_path:
    :return:
    """
    if not os.path.exists(test_project_path):
        # 判断目录决定创建
        os.makedirs(test_project_path)

    file_abs_path = os.path.join(test_project_path, 'debugtalk.py')
    if not os.path.exists(file_abs_path):
        # 读取debugtalk
        try:
            debugtalk = Debugtalk.objects.get(project_id=project_id).debugtalk
        except Debugtalk.DoesNotExist:
            debugtalk = ''

        # 读取公共函数
        with open(os.path.join(settings.BASE_DIR, 'httprunner_extend_functions.py'), encoding='utf-8') as f:
            code = f.read()

        # 读取环境变量
        env_vars_content = EnvInfo.objects.get(base_url=base_url).env_vars

        # 拼接文件内容  变量优先级: 环境变量 > debugtalk > 公共函数
        file_content = code + '\n' + debugtalk + '\n' + env_vars_content

        to_file(file_abs_path, file_content)


def load_testcase(case_id, test_project_path, base_url=None):
    """
    加载数据库中用例数据到目标目录中
    :param case_id:
    :param test_root_path:
    :param base_url:
    :return:
    """
    if not os.path.exists(test_project_path):
        # 判断目录决定创建
        os.makedirs(test_project_path)

    # 单个用例数据结果
    testcase_info = []
    config = {
        'config': {
            'name': '',
            'request': {
                'base_url': base_url or ''
            },
            # 加载全局变量
            'variables': load_env()
        }
    }
    # 添加配置信息到用例信息前
    testcase_info.append(config)

    if isinstance(case_id, int):
        # 获取请求对象数据
        try:
            testcase_obj = TestCase.objects.get(id=case_id)
        except TestCase.DoesNotExist:
            resp = {
                'message': '用例ID<{}>不存在'.format(case_id)
            }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)

        # 获取用例信息
        name = testcase_obj.name
        before = eval(testcase_obj.before)
        after = eval(testcase_obj.after)
        project = testcase_obj.project
        module = testcase_obj.module
        request_info = eval(testcase_obj.request.replace('true', 'True').replace('false', 'False'))
        params_files = eval(testcase_obj.params_files)
    else:
        # debug请求
        # 获取用例信息
        name = case_id.get('name')
        before = eval(case_id.get('before')) if case_id.get('before') else None
        after = eval(case_id.get('after')) if case_id.get('after') else None
        project = Project.objects.get(id=case_id.get('project'))
        module = Module.objects.get(id=case_id.get('module'))
        request_info = eval(case_id.get('request').replace('true', 'True').replace('false', 'False'))
        params_files = eval(case_id.get('params_files'))

    # 加载debugtalk文件
    load_debugtalk(test_project_path, project_id=project.id, base_url=base_url)

    # config.name
    config['config']['name'] = name

    # 用例保存路径
    testcase_path = os.path.join(test_project_path, module.module_name)
    if not os.path.exists(testcase_path):
        os.mkdir(testcase_path)

    def get_pre_and_post_req(info):
        """
        获取前后置操作，递归获取，深度优先
        :param info: 前置或后置步骤列表
        :return: 前后置步骤列表
        """
        # info 样例数据：[['3', 'getblog_setting'], ['4', 'xxxxxxxblogs']]
        nonlocal error_msg
        nonlocal params_files
        return_list = []

        for single_req in info:
            req_id = single_req[0]
            try:
                tc_object = TestCase.objects.get(id=req_id)
                current_before = eval(tc_object.before)
                current_after = eval(tc_object.after)
                current_params_file = eval(tc_object.params_files)
                current_req = eval(tc_object.request.replace('true', 'True').replace('false', 'False'))
                temp_list = []
                # 前置步骤非空则递归，返回结果为列表，使用extend增加到临时列表中
                if current_before:
                    temp_list.extend(get_pre_and_post_req(current_before))
                # 当前请求加到临时列表中
                temp_list.append(current_req)
                # 同前置步骤
                if current_after:
                    temp_list.extend(get_pre_and_post_req(current_after))
                # 追加前后置步骤的参数文件
                if current_params_file:
                    params_files.extend(current_params_file)
                # 当前前置步骤的前中后步骤作为整体拓展到结果列表中
                return_list.extend(temp_list)

            except TestCase.DoesNotExist:
                error_msg = '前（后）置步骤《{}》不存在,用例《{}》不执行'.format(single_req[1], name)
                logger.error(error_msg)
                break
        # 遍历完成后返回结果列表
        return return_list

    # 检查是否需要参数文件和前后置步骤
    error_msg = ''  # 如果出现下面的错误，则跳过当前的用例不执行（不加载到执行目录）

    # 获取前置步骤
    if before:
        testcase_info.extend(get_pre_and_post_req(before))
    # 加载当前请求数据到用例信息中
    testcase_info.append(request_info)
    # 获取后置步骤
    if after:
        testcase_info.extend(get_pre_and_post_req(after))

    for filename in  params_files:
        # 如测试目录下已经有同名参数文件,跳过
        params_file_test_path = os.path.join(testcase_path, filename)
        if os.path.exists(params_file_test_path): continue
        # 获取参数文件在服务器的存放路径, 并copy到测试目录
        try:
            params_file_path = ParamsFile.objects.get(project=project, file__contains=filename).file
            params_file_path = os.path.join(settings.BASE_DIR, str(params_file_path))
            shutil.copy(params_file_path, params_file_test_path)
        except ParamsFile.DoesNotExist:
            error_msg = '项目《{}》下不存在参数文件《{}》记录，用例《{}》不执行。'.format(project.project_name, filename, name)
            logger.error(error_msg)
        except FileNotFoundError as e:
            error_msg = '服务端中该项目《{}》参数文件《{}》不存在，复制失败;用例《{}》不执行。'.format(project.project_name, filename, name)
            logger.error(error_msg)
    if not error_msg:
        to_yaml_file(os.path.join(testcase_path, name + '.yml'), testcase_info)


def prepare_case(task_info, test_root_path):

    # 判断运行用例的集合
    case_list = []
    for key, value in task_info['case_list'].items():
        if key == 'case':
            case_list = value
        elif key == 'module':
            for mod_id in value:
                case_list.extend([item['id'] for item in TestCase.objects.filter(module_id=mod_id).values('id')])
        else:
            for proj_id in value:
                case_list.extend([item['id'] for item in TestCase.objects.filter(project_id=proj_id).values('id')])

    # 测试环境
    try:
        base_url = EnvInfo.objects.get(pk=task_info['env']).base_url
    except EnvInfo.DoesNotExist:
        pass

    # 加载全部用例
    for case_id in case_list:
        try:
            # 获取项目名
            project = TestCase.objects.get(pk=case_id).project
            test_project_path = os.path.join(test_root_path, project.project_name)
            load_testcase(case_id, test_project_path, base_url)
        except TestCase.DoesNotExist:
            pass

    return len(case_list)

def run_case(test_root_path, gen_report=False, report_name=None):
    """
    调用httprunner接口，运行已加载的用例
    :param test_root_path:
    :return:
    """
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    runner.run(test_root_path)
    shutil.rmtree(test_root_path)
    if gen_report:
        report_name = report_name or None
        runner.gen_html_report(html_report_name=report_name)
        return {
            'summary': runner.summary,
            'report': report_name
        }
    return runner.summary
