import io
import json
import yaml


def to_yaml_file(yaml_file, data):
    """
    写入yaml文件
    :param yaml_file:
    :param data:
    :return:
    """
    with io.open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, indent=4, default_flow_style=False, encoding='utf-8')


def to_json_file(json_file, data):
    """
    写入json文件
    :param json_file:
    :param data:
    :return:
    """
    with io.open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, separators=(',', ': '), ensure_ascii=False)


def to_file(file_name, data):
    """
    写入文件
    :param python_file:
    :param data:
    :return:
    """
    with io.open(file_name, 'w', encoding='utf-8') as f:
        if isinstance(data, (list, tuple)):
            """可以按行写入"""
            f.writelines(data)
            return None
        f.write(data)
