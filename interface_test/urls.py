"""AutoTest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from interface_test.api import user, env_info, project, debugtalk, params_file, module, testcase, global_var, \
    run_test, report, periodictask, interface_mock, scene_mock
from interface_test.views import check_result, get_all_func, get_dashboard_info, getrefslink, getrefscase, copy_testcase

app_name = 'interface_test'


urlpatterns = (
    path('check/', check_result), # 结果检查
    path('getfuncs/', get_all_func), # 结果检查
    path('debug/', run_test.DebugView.as_view()), # 同步调用
    path('test/', run_test.TestView.as_view()), # 异步调用
    path('run-periodictask/', run_test.RunPeriodicTask.as_view()), # 手动运行（定时）任务
    path('get_dashboard_info/', get_dashboard_info),
    path('get_refs_link/<int:tc_id>/', getrefslink), # 查询用例的引用链
    path('getrefscase/', getrefscase), # 查询引用的用例
    path('copy-testcase/', copy_testcase), # 查询引用的用例
    #
    path('registe/', user.RegView.as_view()),
    path('user/', user.UserView.as_view()),
    path('user/<int:uid>/', user.UserView.as_view()),
    # re_path('^user/(\d+)$/', user.UserRegView.as_view()),
    path('login/', user.LogintView.as_view()),
    path('logout/', user.LogoutView.as_view()),
    # 环境信息
    path('env/', env_info.EnvInfoView.as_view()),
    path('env/<int:pk>/', env_info.EnvInfoDetailView.as_view()),
    # 项目信息
    path('project/', project.ProjectView.as_view()),
    path('project/<int:pk>/', project.ProjectDetailView.as_view()),
    # debugtalk信息
    path('debugtalk/', debugtalk.DebugtalkView.as_view()),
    path('debugtalk/<int:pk>/', debugtalk.DebugtalkDetailView.as_view()),
    # 参数文件信息
    path('paramsfile/', params_file.ParamsFileView.as_view()),
    path('paramsfile/<int:pk>/', params_file.ParamsFileDetailView.as_view()),
    # 模块信息
    path('module/', module.ModuleView.as_view()),
    path('module/<int:pk>/', module.ModuleDetailView.as_view()),
    # 全局变量信息
    path('globalvar/', global_var.GlobalVarView.as_view()),
    path('globalvar/<int:pk>/', global_var.GlobalVarDetailView.as_view()),
    # 用例信息
    path('testcase/', testcase.TestCaseView.as_view()),
    path('testcase/<int:pk>/', testcase.TestCaseDetailView.as_view()),
    # 报告信息
    path('report/', report.ReportView.as_view()),
    path('report/<int:pk>/', report.ReportDestroyView.as_view()),
    # 定时任务
    path('task/', periodictask.PeriodicTaskView.as_view()),
    path('task/<int:pk>/', periodictask.PeriodicTaskDetailView.as_view()),
    # 接口mock和场景mock
    path('interface/', interface_mock.InterfaceMockView.as_view()),
    path('interface/<int:pk>/', interface_mock.InterfaceMockDetailView.as_view()),
    path('scene/', scene_mock.SceneMockView.as_view()),
    path('scene/<int:pk>/', scene_mock.SceneMockDetailView.as_view()),
)
