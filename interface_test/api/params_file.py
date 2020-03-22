from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from interface_test.models import ParamsFile, Project, FilePathHasExist
from interface_test.serializer import ParamsFileSerializer
from interface_test.permission import IsAdmin
import logging


logger = logging.getLogger(__name__)

import os
from rest_framework.views import APIView


file_encoding = 'utf8'

def delete_file(file_path):
    """
    文件删除成功,或者不存在.返回True
    删除失败,返回False
    :param file_path:
    :return:
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception:
            return False
    return True


class ParamsFileView(generics.ListCreateAPIView):
    """
    全部查询和创建
    """
    serializer_class = ParamsFileSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = ParamsFile.objects.all().order_by('-create_time')
        project = self.request.query_params.get('project', None)
        if project is not None:
            queryset = queryset.filter(project__id=project)
        return queryset

    def get(self, request, *args, **kwargs):
        """
        因为已经启用了分页，如果不写page参数，默认会返回page=1的结果，所以一定要带page参数来控制
        如果接口参数page=None，则返回全部数据，如果为正整数，返回对应页数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if request.query_params.get('page') == 'None':
            self.pagination_class = None

        return super().get(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        logger.info('文件上传请求参数：{}'.format(request.data))
        resp = {}
        data = {}
        data['file'] = request.FILES.get('file')
        data['author'] = request.data.get('author') or 'admin'
        # 打开认证后,应该从下面获取上传者信息
        # author = request.user
        try:
            data['project'] = Project.objects.get(pk=int(request.data.get('project')))
            params_file_obj = ParamsFile.objects.create(**data)
            serializer = ParamsFileSerializer(params_file_obj)
        except FilePathHasExist  as e:
            logger.error(e)
            resp['message'] = '该项目下已存在同名文件{}'.format(data['file'])
            stat = status.HTTP_400_BAD_REQUEST
        except Project.DoesNotExist:
            resp['message'] = '所选项目<{}>不存在'.format(request.data.get('project'))
            logger.error(resp['message'])
            stat = status.HTTP_400_BAD_REQUEST
        else:
            resp['data'] = serializer.data
            stat = status.HTTP_201_CREATED
        return Response(resp, status=stat)


class ParamsFileDetailView(APIView):
    """
    参数文件信息单查询、修改
    """
    def get(self, request, pk):
        """
        获取单个文件的信息
        如果要获取文件内容,使用content参数,为1,返回内容;为0不返回内容; 默认为1
        :param request:
        :param pk:
        :return:
        """
        logger.info('文件查询参数：{}'.format(request.query_params))
        try:
            obj = ParamsFile.objects.get(pk=pk)
            serializer = ParamsFileSerializer(obj)
            # 参数控制返回是否带文件内容
            content = request.query_params.get('content', '1')
            if content != '0':
                with open(obj.file.name, encoding=file_encoding) as f:
                    code = f.read()
                resp = { 'content': code, 'model': serializer.data}
                return Response(resp, status=status.HTTP_200_OK)
        except ParamsFile.DoesNotExist:
            return Response({'message': '该数据不存在'}, status=status.HTTP_400_BAD_REQUEST)
        except FileNotFoundError as e:
            logger.error(e)
            return Response({'message': '文件不存在或已删除'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        删除文件记录和文件
        :param request:
        :param pk:
        :return:
        后面要增加用例引用文件时不能删除文件的保存
        """
        try:
            obj = ParamsFile.objects.get(pk=pk)
            if delete_file(obj.file.name):
                obj.delete()
            else:
                return Response({'message': '文件删除失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ParamsFile.DoesNotExist:
            return Response({'message': '该数据不存在'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        修改文件内容, 带json
        {
            "content":"update content"
        }
        :param request:
        :param pk:
        :return:
        """
        try:
            obj = ParamsFile.objects.get(pk=pk)
            serializer = ParamsFileSerializer(obj)
            code = request.data.get('content', '')
            with open(obj.file.name, 'w', encoding=file_encoding) as f:
                f.write(code)
            obj.save()  # 为了更新update_time字段
        except ParamsFile.DoesNotExist:
            return Response({'message': '该数据不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data, status=status.HTTP_200_OK)
