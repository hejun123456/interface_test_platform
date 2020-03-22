from django.test import TestCase

# Create your tests here.

from rest_framework.test import APIRequestFactory

from interface_test.api.project import ProjectView
from interface_test.api.user import RegView, LogintView
from time import time

# Using the standard RequestFactory API to create a form POST request

class RegisteTestCase(TestCase):
    def setUp(self):
        # Project.objects.create(name="lion", sound="roar")
        self.view = RegView.as_view()

    def test_project_create(self):
        factory = APIRequestFactory()
        data = {
            'username': 'zrb' + str(time()),
            'password': '123'
        }
        request = factory.post('/registe/', data=data, format='json')
        response = self.view(request)
        self.assertEqual(response.data.get('message'), '注册成功', '注册请求失败')
        self.assertEqual(response.status_code, 200, '注册请求响应码错误')

    def tearDown(self):
        pass


class ProjectTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.reg_view = RegView.as_view()
        self.log_view = LogintView.as_view()
        self.view = ProjectView.as_view()
        self.username = 'zrb' + str(time())
        self.password = '123'
        self.reg_data = {
            'username': self.username,
            'password': self.password
        }
        request = self.factory.post('/registe/', data=self.reg_data, format='json')
        response = self.reg_view(request)
        self.assertEqual(response.data.get('message'), '注册成功', '注册请求失败')
        self.assertEqual(response.status_code, 200, '注册请求响应码错误')

        login_request = self.factory.post('/login/', data=self.reg_data, format='json')
        response = self.log_view(login_request)
        self.token = response.data.get('token')
        print('token: ', self.token)

        self.project_data = {
            'project_name': 'interface test',
            'leader': 'zrb',
            'test_user': 'zrb',
            'dev_user': 'li4',
            'description': '测试',
        }

    def test_project_create(self):
        request = self.factory.post('/project/', data=self.project_data, format='json', HTTP_TOKEN=self.token)
        response = self.view(request)
        print(request.headers)
        print(response.data)

    def tearDown(self):
        pass