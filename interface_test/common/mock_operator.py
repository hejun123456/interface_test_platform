import os
from interface_test_platform import settings
from interface_test.models import InterfaceMock, SceneMock
from interface_test.common.file_operate import to_json_file

mock_data_path = os.path.join(settings.BASE_DIR, 'mock_data')
if not os.path.exists(mock_data_path):
    os.makedirs(mock_data_path)

mock_settings = os.path.join(mock_data_path, 'settings.json')
if not os.path.exists(mock_settings):
    to_json_file(mock_settings, [])

import logging
logger = logging.getLogger(__name__)

"""
接口和场景的开关操作，只处理数据的更新，不会直接运行系统命令开关moco(手工运行)
"""


def read_mock(mock_file):
    """
    读取data_list数据(settings或接口文件)
    :param data_list:
    :return:
    """
    with open(mock_file) as f:
        data_list = eval(f.read())
    return data_list


def interface_start(data):
    """
    接口实例数据，包括外键数据集
    数据文件以本数据的id命名， ${id}.json
    settings: [
        {"include": "${id}.json"}
    ]
    :return:
    """
    # 数据文件以本数据的id命名， ${id}.json
    file_name = str(data['id']) + '.json'
    data_file = os.path.join(mock_data_path, file_name)
    # 写入数据文件
    scenes = SceneMock.objects.filter(interface_id=data['id'], enabled=True)# data.get('scenes', [])
    # scenes = [{'description': str(scene['id']), 'request': eval(scene['request']), 'response': eval(scene['response'])}
    #           for scene in scenes if scene['enabled']]
    tmp_list = []
    for scene in scenes:
        request = eval(scene.request)
        request['uri'] = data['uri'].strip()
        tmp_list.append({'description': str(scene.id), 'request': request, 'response': eval(scene.response)})
    to_json_file(data_file, tmp_list)
    # 先读取，再写入settings
    settings_list = read_mock(mock_settings)
    if not [x for x in settings_list if x['include'] == file_name]:
        # 如果没有找到本接口记录，则追加
        settings_list.append({'include': file_name})
        to_json_file(mock_settings, settings_list)


def interface_stop(interface_id):
    file_name = str(interface_id) + '.json'
    settings_list = read_mock(mock_settings)
    try:
        # 直接删除，没有则报错不处理，文件也不会被修改
        settings_list.remove({'include': file_name})
        to_json_file(mock_settings, settings_list)
    except ValueError as e:
        logger.error('接口关闭错误：')
        logger.error(e)

    try:
        # 删除接口文件
        os.remove(os.path.join(mock_data_path, file_name))
    except FileNotFoundError as e:
        logger.error('接口关闭错误：')
        logger.error(e)


def scene_start(data):
    """
    读取具体的接口文件
    :param data:
    :return:
    """
    interface = data['interface']
    file_name = os.path.join(mock_data_path, str(interface) + '.json')
    try:
        scenes_list = read_mock(file_name) # 如果接口没启用，无文件
        uri = InterfaceMock.objects.get(pk=interface).uri.strip()
        if not [x for x in scenes_list if x['description'] == str(data['id'])]:
            # 如果没有找到本接口记录，则追加
            request = eval(data['request'])
            request['uri'] = uri
            scenes_list.append({'description': str(data['id']), 'request': request, 'response': eval(data['response'])})
            to_json_file(file_name, scenes_list)
    except FileNotFoundError:
        # 无文件，说明接口没启用
        pass


def scene_stop(data):
    interface = data['interface']
    file_name = os.path.join(mock_data_path, str(interface) + '.json')
    try:
        scenes_list = read_mock(file_name)
        uri = InterfaceMock.objects.get(pk=interface).uri.strip()
        # 直接删除，没有则报错不处理，文件也不会被修改
        request = eval(data['request'])
        request['uri'] = uri
        scenes_list.remove({'description': str(data['id']), 'request': request, 'response': eval(data['response'])})
        to_json_file(file_name, scenes_list)
    except ValueError:
        pass
    except FileNotFoundError:
        # 无文件，说明接口没启用
        pass
