import os
from django.db import models

# Create your models here.

from django.core.files.storage import FileSystemStorage
from djcelery.models import PeriodicTask


class FilePathHasExist(Exception):
    """
    文件名(路径)已经存在
    作用:文件的保存路径下有同名时,抛出该异常
    """
    pass


class mystorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        """
        此方法在Storage类中，主要用在有同名文件时返回带随机后缀的可用文件名
        所以只要复写此方法，文件路径同名时抛出异常，并在view中捕获处理即可。
        ParamsFile的属性file在数据库中是文件路径，是唯一的。同名时会报唯一性错误。
        以此达到不能上传同名文件的效果
        :param name:
        :param max_length:
        :return:
        """
        if self.exists(name):
            # 如果下面这句注释掉了，程序就会死循环
            # 如果文件名已存在，抛出异常
            raise FilePathHasExist('文件名{}已存在'.format(name))
        return name


class BaseModel(models.Model):
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    role_choices = {
        (0, '普通用户'),
        (1, '管理员')
    }
    role = models.SmallIntegerField('用户角色', choices=role_choices, default=0)
    username = models.CharField('用户名', max_length=50, unique=True)
    password = models.CharField('密码', max_length=50)
    email = models.EmailField('邮箱地址', blank=True)

    def __str__(self):
        return self.username


class Token(BaseModel):
    user = models.OneToOneField(to='User', on_delete=models.CASCADE)
    token = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.token


class EnvInfo(BaseModel):
    """
    保存环境信息，包括：
    1、环境域名，可能存在多个域名
    2、与环境强相关的数据
    """
    env_name = models.CharField(max_length=50, unique=True)
    base_url = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=100, blank=True)
    is_valid = models.BooleanField('启用/禁用', default=True, blank=True)
    env_vars = models.TextField('环境信息（变量）配置文件', blank=True,
                                default='# 环境信息\n# 1、对运行环境有依赖的基础数据。' +
                                        '\n# 2、系统存在前后台多个域名时配置域名' +
                                        '\n# 应用举例：流程中多个请求指向不同域名，请求中应该引用所配置的域名变量' +
                                        '\n# 本配置文件为python模块，可以配置任意格式的python变量或执行python代码')

    def __str__(self):
        return self.env_name


class Project(BaseModel):
    project_name = models.CharField('项目名称', max_length=100, unique=True)
    leader = models.CharField('负责人', max_length=100)
    test_user = models.CharField('测试人员', max_length=100, blank=True)
    dev_user = models.CharField('开发人员', max_length=100, blank=True)
    description = models.TextField('项目描述',blank=True)

    def __str__(self):
        return self.project_name


class Debugtalk(BaseModel):
    """
    一个项目只有一个debugtalk.py
    """
    project = models.OneToOneField(to='Project', on_delete=models.CASCADE, related_name='debugtalk')
    debugtalk = models.TextField('文件内容', blank=True, default='#debugtalk.py')

    def __str__(self):
        return self.debugtalk[:100]


class ParamsFile(BaseModel):
    """
    一个项目可有多个参数文件.py
    """
    def get_file_path(self, filename):
        """
        self是本类FileField定义模型的一个未保存到数据库的实例，可以获取本类的属性
        https://docs.djangoproject.com/en/1.11/ref/models/fields/#django.db.models.FileField
        :param filename:上传的文件名
        :return:
        """
        return os.path.join('static', 'upload', self.project.project_name, filename)

    project = models.ForeignKey(to='Project', on_delete=models.CASCADE, related_name='params_file')
    file = models.FileField(upload_to=get_file_path, unique=True, storage=mystorage())
    author = models.CharField('上传者/作者', max_length=50)

    def __str__(self):
        return self.file.name


class Module(BaseModel):
    module_name = models.CharField('模块名称', max_length=100)
    project = models.ForeignKey(to='Project', on_delete=models.CASCADE, related_name='module')
    test_user = models.CharField('测试人员', max_length=100, blank=True)
    description = models.TextField('模块描述',blank=True)

    class Meta:
        unique_together = ('module_name', 'project')

    def __str__(self):
        return self.module_name


class TestCase(BaseModel):
    type_choices = {
        (0, '配置'),
        (1, '请求')
    }
    type = models.SmallIntegerField('test/config', choices=type_choices, default=1)
    name = models.CharField('用例/配置名称', max_length=100, unique=True)
    project = models.ForeignKey(to='Project', on_delete=models.CASCADE, related_name='testcase')
    module = models.ForeignKey(to='Module', on_delete=models.CASCADE, related_name='testcase')
    before = models.CharField('前置配置或步骤', max_length=1024, default='[]')
    after = models.CharField('后置步骤', max_length=1024, default='[]')
    author = models.CharField('编写人员', max_length=50)
    request = models.TextField('请求信息')
    params_files = models.CharField('参数文件列表', max_length=256, default='[]')

    # 用例名全局唯一
    # class Meta:
    #     unique_together = ('project', 'module', 'name')
    def __str__(self):
        return self.name


class GlobalVar(BaseModel):
    """
    保存与环境无关的全局通用变量
    """
    var_name = models.CharField('变量名', max_length=50, unique=True)
    var_value = models.CharField('变更值', max_length=256)
    description = models.TextField('参数描述', blank=True)

    def __str__(self):
        return self.var_name


class Report(BaseModel):
    report_name = models.CharField('任务名', max_length=255, unique=True)
    task_id = models.CharField('任务id', max_length=40)
    start_at = models.DateTimeField('开始时间', auto_now_add=True)
    duration = models.FloatField('运行时长', default=0)
    result = models.CharField('任务结果', max_length=10, default='运行中...')
    case_sum = models.IntegerField('用例总数', default=0)
    case_pass = models.IntegerField('用例成功数', default=0)
    case_error = models.IntegerField('用例错误数', default=0)
    case_failure = models.IntegerField('用例失败数', default=0)
    case_skipped = models.IntegerField('用例跳过数', default=0)
    description = models.TextField('任务描述', blank=True)
    summary = models.TextField('运行结果', blank=True)
    status = models.BooleanField('是否被删除', default=True, blank=True)

    def __str__(self):
        return self.report_name


class TaskExtend(models.Model):
    """
    拓展PeriodicTask模型
    """
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    email_list = models.CharField('邮箱列表', max_length=2048, default='[]')
    author = models.CharField('创建人', max_length=100, default='')
    project = models.IntegerField('任务所选项目', default=0)
    periodic_task = models.OneToOneField(PeriodicTask, on_delete=models.CASCADE, related_name='taskextend')


class InterfaceMock(BaseModel):
    name = models.CharField('接口名', max_length=100, unique=True)
    uri = models.CharField('uri', max_length=256)
    description = models.TextField('简要描述', blank=True)
    enabled = models.BooleanField('启用/禁用', default=False, blank=True)

    def __str__(self):
        return self.name


class SceneMock(BaseModel):
    name = models.CharField('场景名', max_length=100)
    description = models.TextField('简要描述', blank=True)
    enabled = models.BooleanField('启用/禁用', default=False, blank=True)
    request = models.TextField('请求json')
    response = models.TextField('响应json')
    interface = models.ForeignKey(to='InterfaceMock', on_delete=models.CASCADE, related_name='scene')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('interface', 'name')
