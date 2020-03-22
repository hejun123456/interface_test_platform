import datetime
import json
import re

from PIL import Image
from rest_framework import status
from rest_framework.response import Response

from interface_test.models import TestCase


def timestamp_to_datetime(summary, type=True):
    if not type:
        time_stamp = int(summary["time"]["start_at"])
        summary['time']['start_datetime'] = datetime.datetime. \
            fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

    for detail in summary['details']:
        try:
            time_stamp = int(detail['time']['start_at'])
            detail['time']['start_at'] = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass

        for record in detail['records']:
            try:
                time_stamp = int(record['meta_data']['request']['start_timestamp'])
                record['meta_data']['request']['start_timestamp'] = \
                    datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
    return summary


def bytes2str(data):
    """
    如果data中包含有bytes类型数据，在使用JsonResponse时会报错
    函数用于把请求响应中的bytes转成str
    :param data:字典类型
    :return:
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, bytes):
                data[key] = value.decode()
            elif isinstance(value, dict):
                data[key] = bytes2str(value)
            elif isinstance(value, list):
                for i in range(len(value)):
                    value[i] = bytes2str(value[i])
                data[key] = value
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = bytes2str(data[i])
    return data


def python2js(value, check_list=(None, True, False)):
    """
    把check_list中的值从python类型转成js(json)类型，以适配前端显示
    :param value:
    :param check_list:
    :return:
    """
    if check_list is not None and value in check_list:
        value = json.dumps(value)
    else:
        value = str(value)
    return value


def tidy_tree_data(data, tree_list, parent_path=None):
    '''
    此函数为递归函数, 用于整理返回给前端显示的树形结果数据
    初始的data为响应数据response，是字典类型
    所以初始化数据不能是字典或列表以外的类型
    :parent_path：为None即表示为顶层。子层向下传入时应该把当前parent_path+本身路径(key)
    :param data:
    :param tree_list:传入要保存数据的列表，建议传[]（适配ztree框架的数据要求）
    :return:
    '''
    if isinstance(data, list):
        for i, v in enumerate(data):
            '''
            假设响应数据如下：
            [
                {
                    "id": 53,
                    "title": "xxxxxxxxxx",
                    "content": "<p>123</p>",
                    "author": "123",
                    "pub_date": "2019-07-24T13:45:33.755000"
                },
                {
                    "id": 54,
                    "title": "324",
                    "content": "<p>234</p>",
                    "author": "234",
                    "pub_date": "2019-07-24T13:45:44.484000"
                }
            ]
            如果想取出第一条数据的id,httprunner提取数据，则使用json.0.id
            所以在前端做结果树形显示时，把列表数据的索引作为一级，也是为了后面做数据自动提取作铺垫。
            '''
            # 保存本次节点数据的字典对象
            node = {}
            if isinstance(v, (str, int, float, bool)):
                node['title'] = str(i) + '-->' + python2js(v)
                node['expect'] = v
            else:
                node['title'] = i
                sub_parent_path = str(i) if parent_path is None else parent_path + '.' + str(i) # 下一层的父路径
                node['children'] = tidy_tree_data(v, [], parent_path=sub_parent_path)
            # 保存本数据节点的路径(父路径.本节点路径)
            node['path'] = str(i) if parent_path is None else parent_path + '.' + str(i)
            node['name'] = i
            if node:
                tree_list.append(node)
    elif isinstance(data, dict):
        for key, value in data.items():
            if key in ['content_type', 'content_size', 'response_time_ms', 'elapsed_ms']:
                # 这三个字段在httprunner中不支持提取，所以过滤掉。
                continue
            # 保存本次节点数据的字典对象
            node = {}
            # 下一层的父路径
            sub_parent_path = key if parent_path is None else parent_path + '.' + key
            if isinstance(value, (list, dict, tuple)):
                # 列表或字典 递归解释
                node['children'] = tidy_tree_data(value, [], parent_path=sub_parent_path)
                node['title'] = key if node['children'] else key + '-->' + python2js(value)
            else:
                if key in ['text', 'content']:
                    '''
                    text类型为字节和 content类型为字串，但是为了适配前端显示，把这两字段的内容解释成功字典或列表
                    如果解释失败，有可以是内容为空，或者包含不可解释成python对象的内容。
                    此时直接按字串输出
                    '''
                    try:
                        value = re.sub(r':\s*null\s*,', ': None,', value if isinstance(value, str) else value.decode())
                        value = eval(value)
                        # node['name'] = key
                        if isinstance(value, (list, dict)):
                            node['children'] = tidy_tree_data(value, [], parent_path=sub_parent_path)
                            node['title'] = key if node['children'] else key + '-->[]'
                        else:
                            node['title'] = key + '-->' + python2js(value)
                            node['expect'] = value
                    except Exception:
                        node['title'] = key + '-->' + python2js(value)
                        node['expect'] = value
                else:
                    # 字串直接输出
                    node['title'] = key + '-->' + python2js(value)
                    node['expect'] = value
            # 保存本数据节点的路径(父路径.本节点路径)
            node['path'] = key if parent_path is None else parent_path + '.' + key
            node['name'] = key
            if node:
                tree_list.append(node)
    return tree_list


def second2hms(second):
    """
    把秒数转换成时分秒格式
    :param second:
    :return:
    """
    second = float(second)

    h = int(second / 3600)
    second = second % 3600

    m = int(second / 60)
    s = round(second % 60, 2)

    t = str(s) + 's'
    if m:
        t = '{0}m {1}s'.format(str(m), str(s))
    if h:
        t = '{0}h {1}m {2}s'.format(str(h), str(m), str(s))

    return t


def thumbnail(path, new_path=None, q=100):
    '''压缩并保存到文件'''
    img = Image.open(path)
    w, h = img.size
    width, height = w * q // 100, h * q // 100
    img.thumbnail((width, height))

    if new_path:
        img.save(new_path, img.format)
    else:
        img.save(path, img.format)


def testcase_summary(summary):
    successes = 0
    failures = 0
    errors = 0
    skipped = 0
    for testcase in summary['details']:
        if testcase['success']:
            successes += 1
        else:
            if testcase['stat']['errors'] > 0:
                errors += 1
            else:
                failures += 1
    return successes, failures, errors, skipped


def top10error(summary):
    pattern = r'(.*\.)?(.*?Error:(?:.*?Failure)?)(.+)'  # 提取错误原因正则表格式
    successes = 0
    failures = 0
    errors = 0
    top10errors = {}
    for item in summary['details']:
        # 提取用例执行情况
        if item['success']:
            successes += 1
        else:
            if item['stat']['errors'] > 0:
                errors += 1
            else:
                failures += 1
            # 对错误用例原因统计
            for record in item['records']:
                if record['status'] != 'success':
                    all_list = re.findall(pattern, record['attachment'])
                    m = all_list[-1]  # 取最后一个报错原因
                    if top10errors.get(m[1]):
                        # 已记录本错误原因
                        top10errors[m[1]][0] += 1
                    else:
                        # 未记录本错误原因
                        top10errors[m[1]] = [1, m[2]]  # [errorNum, errorDetail]
                    break  # 只取每个用例中第一个报错请求

    # 计算各错误率
    wrong_total = failures + errors
    for key, value in top10errors.items():
        # [errorNum, errorDetail, errorRate]
        top10errors[key].append('%.2f' % (value[0] / wrong_total * 100) + '%')

    # 错误原因排序
    # [('errorName', [errorNum, errorDetail, errorRate])...]
    top10errors = sorted(top10errors.items(), key=lambda x: x[1][0], reverse=True)[:10]  # 取前10，不足10，取全部

    data_list = []
    for item in top10errors:
        data_list.append({
            'err_name': item[0],
            'err_sum': item[1][0],
            'err_rate': item[1][2],
            'err_detail': item[1][1]
        })

    return data_list, successes, failures, errors


def get_refs_link(testcase_id, current=False):
    """
    获取当前用例的引用链, 本函数可递归
    :param testcase_id:
    :param current: 标识是否为当前请求，默认为False
    :return: 返回引用链的列表，格式如：[[id, before_tc_name], [id, current_tc_name, True],  [id, after_tc_name]]
    """
    # 保存引用链数据
    refs_link = []

    # 1、获取当前用例
    current_testcase_obj = TestCase.objects.get(pk=testcase_id)
    # 2、获取前置、后置用例
    before_link = eval(current_testcase_obj.before)
    after_link = eval(current_testcase_obj.after)
    # 3、如果有前后置用例，则递归，否则返回当前用例id和name，按前中后顺序拓展结果列表并返回
    if before_link:
        for item in before_link:
            refs_link.extend(get_refs_link(item[0]))

    current_request = [testcase_id, current_testcase_obj.name]
    if current:
        current_request.append(True)

    refs_link.extend([current_request]) # 添加当前用例到引用链中

    if after_link:
        for item in after_link:
            refs_link.extend(get_refs_link(item[0]))

    return refs_link


def check_testcase_isRecursion(case_id, refs_list):
    """
    检查运行的用例是否存在循环引用，是则True，否则False
    :param case_id: 当前用例的id
    :param ref_list: 用例的引用用例列表，数据格式如: [[2, 'casename1'], [33, 'casename2']]
    :return:
    """
    try:
        for case in refs_list:
            case_link = get_refs_link(case[0])
            if '[{},'.format(case_id) in str(case_link):
                return True
    except RecursionError:
        return True
    return False


"""
定义common_put/common_post方法主要是为了方便由后端统一返回的自定义错误提示语，避免非必要的覆写restful框架方法，减少代码量
"""
def common_post(self, request, error_msg='', *args, **kwargs):
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response({'message': error_msg, 'detail': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


def common_put(self, request, error_msg='', *args, **kwargs):
    data = request.data
    obj = self.queryset.filter(id=data.get('id')).first()
    serializer = self.serializer_class(obj, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response({'message': error_msg, 'detail': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


if __name__ == '__main__':
    pass
