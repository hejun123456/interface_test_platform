from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, EnvInfo, Project, Debugtalk, ParamsFile, Module, TestCase, GlobalVar, Report, TaskExtend, \
    InterfaceMock, SceneMock
from djcelery.models import PeriodicTask


class UserSerializer(serializers.ModelSerializer):
    """
    用户信息序列化
    其中密码为只写，不序列化
    """
    role_choices = {
        (0, '普通用户'),
        (1, '管理员')
    }
    password = serializers.CharField(write_only=True)
    # role字段不接受用户设置
    role = serializers.ChoiceField(choices=role_choices, default=0, required=False, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'role', 'create_time', 'update_time')


class EnvInfoSerializer(serializers.ModelSerializer):
    """
    环境信息序列化
    """
    class Meta:
        model = EnvInfo
        fields = '__all__'


class DebugTalkSerializer(serializers.ModelSerializer):
    """
    项目信息序列化
    """
    project_name = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model = Debugtalk
        fields = '__all__'
        read_only_fields = ('project', 'project_name')


class ParamsFileSerializer(serializers.ModelSerializer):
    """
    参数文件序列化
    """
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    author = serializers.CharField(max_length=50, read_only=True, required=False)
    # 反序列化时不需要显示文件url
    file = serializers.FileField(use_url=False)
    class Meta:
        model = ParamsFile
        fields = '__all__'


class ModuleSerializer(serializers.ModelSerializer):
    """
    模块信息序列化
    """
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    class Meta:
        model = Module
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目信息序列化
    """
    # 在project的信息中显示debugtalk字段
    # debugtalk = DebugTalkSerializer(read_only=True)
    # 可以获取外键模型的单个字段
    # debugtalk = serializers.ReadOnlyField(source='debugtalk.debugtalk')
    # debugtalk_id = serializers.ReadOnlyField(source='debugtalk.id')
    # 在project的信息中显示params_file字段
    # params_file = ParamsFileSerializer(many=True, read_only=True)
    # 在project的信息中显示模块字段
    # module = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class TestCaseSerializer(serializers.ModelSerializer):
    """
    用例信息序列化
    """
    module_name = serializers.CharField(source='module.module_name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    class Meta:
        model = TestCase
        fields = '__all__'


class GlobalVarSerializer(serializers.ModelSerializer):
    """
    用例信息序列化
    """
    class Meta:
        model = GlobalVar
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    """
    用例信息序列化
    """
    result = serializers.CharField(max_length=10, default='运行中...', read_only=True)
    case_sum = serializers.CharField(max_length=10, default='--', read_only=True)

    class Meta:
        model = Report
        fields = '__all__'


class TaskExtendSerializer(serializers.ModelSerializer):
    """
    用例信息序列化
    """
    class Meta:
        model = TaskExtend
        fields = '__all__'


class PeriodicTaskSerializer(serializers.ModelSerializer):
    """
    用例信息序列化
    """
    task_extend = TaskExtendSerializer(source='taskextend', read_only=True)
    # crontab_time = CrontabScheduleSerializer(source='crontab', read_only=True)
    crontab_time = serializers.ReadOnlyField(source='crontab.__str__')
    class Meta:
        model = PeriodicTask
        fields = '__all__'


class SceneMockSerializer(serializers.ModelSerializer):
    """
    用例信息序列化
    """
    class Meta:
        model = SceneMock
        fields = '__all__'


class InterfaceMockSerializer(serializers.ModelSerializer):
    """
    用例信息序列化
    """
    # scenes = SceneMockSerializer(source='scene', read_only=True, many=True)  # 接口和场景的列表分开请求

    class Meta:
        model = InterfaceMock
        fields = '__all__'
