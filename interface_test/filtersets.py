from django_filters import rest_framework as filters
import logging
from interface_test.models import GlobalVar, TestCase, InterfaceMock, SceneMock, Module
from djcelery.models import PeriodicTask

logger = logging.getLogger(__name__)

"""
字段默认使用精准匹配（==），如果需要其他匹配方式，使用lookup_expr定义
"""


class BaseFilter(filters.FilterSet):
    create_time = filters.DateFromToRangeFilter(field_name='create_time')
    update_time = filters.DateFromToRangeFilter(field_name='update_time')


class GlobalVarFilter(BaseFilter):
    var_name = filters.CharFilter(field_name="var_name", lookup_expr='contains')
    var_value = filters.CharFilter(field_name="var_value", lookup_expr='contains')
    description = filters.CharFilter(field_name="description", lookup_expr='contains')
    
    class Meta:
        model = GlobalVar
        fields = ['var_name', 'var_value', 'description']


class TestCaseFilter(BaseFilter):
    name = filters.CharFilter(field_name="name", lookup_expr='contains')
    author = filters.CharFilter(field_name="author", lookup_expr='contains')

    class Meta:
        model = TestCase
        fields = ['name', 'project', 'module', 'author']


class InterfaceMockFilter(BaseFilter):
    name = filters.CharFilter(field_name="name", lookup_expr='contains')
    uri = filters.CharFilter(field_name="uri", lookup_expr='contains')
    description = filters.CharFilter(field_name="description", lookup_expr='contains')

    class Meta:
        model = InterfaceMock
        fields = ['name', 'uri', 'description', 'enabled']


class SceneMockFilter(BaseFilter):
    name = filters.CharFilter(field_name="name", lookup_expr='contains')
    description = filters.CharFilter(field_name="description", lookup_expr='contains')

    class Meta:
        model = SceneMock
        fields = ['name', 'description', 'enabled', 'interface']


class ModuleFilter(BaseFilter):
    module_name = filters.CharFilter(field_name="module_name", lookup_expr='contains')
    test_user = filters.CharFilter(field_name="test_user", lookup_expr='contains')
    description = filters.CharFilter(field_name="description", lookup_expr='contains')

    class Meta:
        model = Module
        fields = ['module_name', 'project', 'description', 'test_user']


class PeriodicTaskFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='contains')
    description = filters.CharFilter(field_name="description", lookup_expr='contains')
    author = filters.CharFilter(field_name="taskextend__author", lookup_expr='contains')
    create_time = filters.DateFromToRangeFilter(field_name='taskextend__create_time')
    update_time = filters.DateFromToRangeFilter(field_name='date_changed')

    class Meta:
        model = PeriodicTask
        fields =  '__all__'