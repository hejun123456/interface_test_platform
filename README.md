BTest platform
==========
前言
----------
BTest是一个接口测试平台, 能帮助用户高效快捷地完成接口自动化用例的开发, 覆盖较为复杂的流程接口场景. 它是我个人业余时间开发的, 难免有不少BUG. 类似这样的平台, 网上已经有很多, 那为什么还要开发这个呢.

在此之前, 实际工作中我基于开源项目HttpRunnerManager做了一些补充性和优化性的二次开发, 渐渐有了自己写个测试平台的想法: 一是为了分享自己的经验和想法,希望能帮助到测试人员更有效的完成工作；二是实践自己的想法, 当是练手.

介绍
-----------
本平台基于django restframwork和vue+iview开发, 驱动框架使用[httprunner(1.5.8)
](https://v1.httprunner.org/) 

***强烈建议使用平台前先了解httprunner的基本用法***

平台特性
------------
- 测试管理：按项目-模块-用例的层级管理，均可批量运行用例
- 用例管理：实现嵌套引用，支持快速调试，以树型展示接口响应数据，并可一键提取结果
- 定时任务：可编辑任务，树型展示用例，方便选择；支持定时和手动触发任务
- 测试报告：包括任务概况、用例详情和top10错误表等内容，简洁地展示任务情况
- 环境管理：保存环境相关的基础数据，便于环境切换，支持python数据类型，支持在线编辑
- 参数化变量：数据量少时可在用例中定义；数据量大时可在文件中定义，支持在线编辑
- mock管理：mock数据按接口-场景的层级管理，均支持独立启/禁用
- 全局变量：方便定义全局通用数据

win开发环境搭建
--------
#### 一、项目结构
1. 项目结构
![BTest接口测试平台20190808.png](https://images.gitee.com/uploads/images/2020/0327/120147_0b3e8204_5217681.png)


2. 目录说明: 前端代码放在后端代码根目录中
![前端目录结构.png](https://images.gitee.com/uploads/images/2020/0327/120148_b158175c_5217681.png)
![后端目录结构.png](https://images.gitee.com/uploads/images/2020/0327/120148_03207018_5217681.png)

#### 二、前端环境
1. 安装node.js/npm并配置环境
2. 配置淘宝镜像 
```
npm install -g cnpm --registry=https://registry.npm.taobao.org
```
3. 安装vue脚本架 
```
cnpm install --global vue-cli
```
4. cd到frontend目录
```
cnpm install
```
5. 运行前端 
```
npm run dev
```

#### 三、后端环境
1. 安装mysql，创建数据库dbname，设置用户名、密码，启动mysql
2. 修改:AutoTest/settings.py里DATABASES字典和邮件配置
```
DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dbname',  # 数据库名
        'USER': 'root',  # 用户名
        'PASSWORD': '123456',  # 密码
        'HOST': '127.0.0.1',  # 数据库ip
        'PORT': '3306',  # 端口默认3306即可
    }
}
EMAIL_SERVER = 'smtp.qq.com' # 邮箱服务器
EMAIL_PORT = 465 # 邮箱服务器端口
EMAIL_SENDER = '123456789@qq.com' # 发件人
EMAIL_PASSWORD = '' # 发件人密码
```
3. 安装erlang和rabbitmq，服务是默认启动的，访问地址 http://localhost:15672/  
默认用户名/密码：guest
```
# 如果没启动使用下面命令
net start RabbitMQ
```
4. 安装python3（本人使用3.7,与celery3.x版本存在冲突命名冲突,需要手动修改celery；或者使用py3.6,可以先参考第7点）
5. 创建虚拟环境(看需要)
```
python -m venv venvName
venvName/Scripts/activate.bat
```
6. 安装三方库
```
pip install -r require.txt
```
7. 更新三方库(celery和httprunner)***(必须操作)***
```
# kumbo库中使用了保留关键字async,与python3.7存在冲突,worker无法运行.
考虑下面三种方式:
1.py<=3.6,则不需要修改任务celery相关内容
-----------------------------------------------------------
2.py>=3.7,手动修改kumbo.async包名,再修改celery中相关引用项(未修改运行会报错,挨个改)
-----------------------------------------------------------
3.py>=3.7,命令升级celery库(升到4.x,不确定celery beat任务实时更新是否有效,未验证):
pip install --upgrade https://github.com/celery/celery/tarball/master
-----------------------------------------------------------

# 更新httprunner,把工程根目录下httprunner_update目录的文件全部替换到当前环境三方包httprunner目录下,对1.5.8版本httprunner做了几处优化.
1.引用函数时参数可以使用python多数数据类型 
详情见 https://www.jianshu.com/p/2b83c1216f57
-----------------------------------------------------------
2.结果提取失败可返回用户定义的默认值 
详情见 https://www.jianshu.com/p/c31a803f1f6a
```
7. 解压phantomjs, 配置环境变量, 命令行输入phantomjs不报错即可
8. 安装jdk，为了运行mock服务，如不需要mock服务可跳过
9. 下载最新版本[moco.jar](https://repo1.maven.org/maven2/com/github/dreamhead/moco-runner/1.1.0/)到工程根目录,新命令行切换到工程根目录,运行服务
```
java -jar moco-runner-X.X.X-standalone.jar http -p 8899 -c mock_data/settings.json
```
10. 切换到工程根目录（manage.py所在目录）
```
python manage.py makemigrations # 生成数据迁移脚本
python manage.py migrate  # 创建表
```
11. 启动后端服务(端口自定义,修改后前端也要配置frontend/src/api/index.js)
```
python manage.py runserver 9999
```
12. 新命令行切换到工程根目录, 分别启动worker、beat、flower
```
celery -A AutoTest worker -l info  #启动worker
celery -A AutoTest beat -l info #启动任务监听
# 上面两命令可以合并: celery -A AutoTest worker -l info -B
celery flower #启动任务后台
```
13. 访问：http://localhost:5555/dashboard 即可查看任务列表和状态
14. 平台地址: http://127.0.0.1:8080/ 
15. django后台是否需要看自己情况

功能介绍
--------
1.  注册新用户,成功后自动登录跳转,前台只能注册为普通用户.而管理员用户可以通过admin后台创建或修改.
![1-登录.png](https://images.gitee.com/uploads/images/2020/0327/120148_a584db28_5217681.png)

2. 首页为数据面板,菜单按测试管理-数据管理-报告管理,划为三个模块
![2-面板.png](https://images.gitee.com/uploads/images/2020/0327/120148_cba05a24_5217681.png)

3. 平台按项目-模块-用例的层级管理,要依次创建对应的条目
![3-项目-模块-用例.png](https://images.gitee.com/uploads/images/2020/0327/120148_84670858_5217681.png)

4. 多数模块都提供了搜索栏
![4-搜索栏.png](https://images.gitee.com/uploads/images/2020/0327/120148_11530f27_5217681.png)

5. 项目/模块/用例均提供了批量运行的方式, 而用例也可以单独运行和快速调试
![5-运行方式.png](https://images.gitee.com/uploads/images/2020/0327/120148_ecefbca9_5217681.png)

6. debugtalk页面, 为每个项目绑定一份自定义函数或变量(下版本改为多项目共用debugtalk), 可在线编辑, 遵循python语法.
![6-1-debug.png](https://images.gitee.com/uploads/images/2020/0327/120148_bd07778d_5217681.png)

7. 用例嵌套引用/快速调试/结果一键提取
![7-1-嵌套引用](https://images.gitee.com/uploads/images/2020/0327/120148_5042f184_5217681.png)
![7-2-快速调试.png](https://images.gitee.com/uploads/images/2020/0327/120148_ed0e465a_5217681.png)
![7-3-一键提取.png](https://images.gitee.com/uploads/images/2020/0327/120148_3d513828_5217681.png)
![7-3-一键提取效果.png](https://images.gitee.com/uploads/images/2020/0327/120149_17f51665_5217681.png)
![7-4-参数化](https://gitee.com/scu-zrb/interface_test_platform/blob/master/image/7-4-params-usage.png)

8. 添加及触发任务
![8-1-添加任务.png](https://images.gitee.com/uploads/images/2020/0327/120148_f6321c37_5217681.png)
![8-2-运行任务.png](https://images.gitee.com/uploads/images/2020/0327/120149_007cf974_5217681.png)

9. 数据管理, 提供多种形式保存用例数据, 做到数据与用例分离的目的
![9-1-数据管理.png](https://images.gitee.com/uploads/images/2020/0327/120149_9ce809e1_5217681.png)

10. MOCK服务基于[moco](https://github.com/dreamhead/moco)运行
![10-1-新增接口.png](https://images.gitee.com/uploads/images/2020/0327/120149_16fe9742_5217681.png)
![10-2-新增场景.png](https://images.gitee.com/uploads/images/2020/0327/120149_b1e33eff_5217681.png)

11. 测试报告及邮件
![11-1-报告详情.png](https://images.gitee.com/uploads/images/2020/0327/120149_eb22d2a0_5217681.png)
![11-2-邮件.png](https://images.gitee.com/uploads/images/2020/0327/120149_a972de04_5217681.png)

下版本待实现
------
1. 增加二级模块; 项目使用目录结构管理（项目-模块-二级模块-用例）
2. celery分布式并发是以任务为执行单位的，如设定的任务用例数量过大，则无法发布分布式的优势，下版本将对过大的任务进行拆分，可真正发挥分布式并发的优势
3. 用例重试机制
4. 任务中错误用例一键重试
5. 用例草稿/回收站
6. 自动化文字用例与脚本关联及场景覆盖率统计