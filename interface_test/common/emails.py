from email.mime.image import MIMEImage

from AutoTest import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from interface_test.common.common import thumbnail
import os

import time
import random
from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.render import make_snapshot
from snapshot_phantomjs import snapshot

import logging


logger = logging.getLogger(__name__)

def gen_pie_chart(data, path):
    """
    :param data:key为label，val为列表：[data, [color]], val[0]为对应数据，val[1]为对应颜色，可不带
    :param path:图片路径
    :return:
    """
    def get_data(data):
        """
        解析数据
        :param data:
        :return:
        """
        labels_value_colors = {
            # data模板
            '错误': [data['errors'], '#ed4014'],
            '失败': [data['failures'], '#ff9900'],
            '跳过': [data['skipped'], '#2db7f5'],
            '成功': [data['successes'], '#19be6b']
        }
        labels = []
        values = []
        colors = []
        for key, val in labels_value_colors.items():
            labels.append(key)
            values.append(val[0])
            if len(val) == 2:
                colors.append(val[1])
        return labels, values, colors or None

    def pie_set_colors():
        """
        图表定义
        :return:
        """
        c = (Pie(opts.InitOpts(width='750px'))
                    .add("", list(zip(labels, values)), radius='65%')
                    .set_colors(colors)
                    .set_global_opts(title_opts=opts.TitleOpts(title="用例执行情况图"))
                    .set_series_opts(label_opts=opts.LabelOpts(font_size=16, formatter="{b}: {c}\n({d}%)"))

                )
        return c

    # # 获取数据
    labels, values, colors = get_data(data)
    # 保存图片
    if not os.path.exists(path):
        os.makedirs(path)

    pic_path = os.path.join(path, str(time.time()) + str(random.randint(0, 1000)) + '.png')

    make_snapshot(snapshot, pie_set_colors().render(), pic_path, is_remove_html=True, pixel_ratio=1)

    thumbnail(pic_path)

    return pic_path


def render_email(content, data):
    """
    因为email模板中带有样式，使用了大括号，而不能使用format函数。所以使用正则进行替换
    :param content:
    :param data:
    :return:
    """
    for key, val in data.items():
        content = re.sub('\{.*' + key + '.*\}', str(val), content)
    return content


def mail(task_name, receivers, pic_path, data):
    """
    :param task_name: 测试任务名
    :param receivers: 收件人列表
    :param pic_path: 测试概况图绝对或相对路径
    :param data: 测试概况数据
    :return:
    """
    msgRoot = MIMEMultipart('related') # 采用related定义内嵌资源的邮件体

    # 定义邮件头信息
    msgRoot['Subject'] = task_name
    msgRoot['from'] = settings.EMAIL_SENDER
    msgRoot['to'] = receivers[0] if len(receivers) == 1 else ','.join(receivers)
    email_template = os.path.join(settings.BASE_DIR, 'interface_test', 'common', 'email_template.html')

    # 渲染html数据
    with open(email_template, encoding='utf8') as f:
        mail_msg = f.read()
    mail_msg = render_email(mail_msg, data)

    msgAlternative = MIMEMultipart('alternative')
    msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))
    msgRoot.attach(msgAlternative)

    # 添加图片附件，指定图片为当前目录
    with open(pic_path, 'rb') as fp:
        msgImage = MIMEImage(fp.read())
    # 定义图片 ID，在 HTML 文本中引用
    msgImage.add_header('Content-ID', '<summarychart>')
    msgRoot.attach(msgImage)

    # 发送邮件
    server = smtplib.SMTP_SSL(settings.EMAIL_SERVER, settings.EMAIL_PORT)  # 发件人邮箱中的SMTP服务器，端口是25
    server.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(settings.EMAIL_SENDER, receivers, msgRoot.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 关闭连接


def tidy_data_from_summary(summary):
    # 渲染表格
    tbody = ''''''
    tr_template = '''
    <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
    </tr>
    '''
    for item in summary['top10error']:
        tbody += tr_template.format(summary['top10error'].index(item)+1,
                                    item['err_name'],
                                    item['err_sum'],
                                    item['err_rate'],
                                    item['err_detail'])
    # 获取测试环境
    data = {
        'report_name': '自动化测试报告',
        'base_url': summary['base_url'],
        'sum': len(summary['details']),
        'start_datetime': summary['time']['start_datetime'],
        'duration': '{:.2f}s'.format(float(summary['time']['duration'])),
        'successes': summary['successes'],
        'failures': summary['failures'],
        'errors': summary['errors'],
        'skipped': 0, # 平台未初始用例的跳过操作,所以不会有跳过用例,临时占位,
        'tbody': tbody
    }
    return data


def send_email(task_name, summary, receivers):
    # data = {
    #     # 'report_name': '自动化测试报告',
    #     # 'sum': 999,
    #     # 'successes': 888,
    #     # 'failures': 10,
    #     # 'errors': 1,
    #     # 'skipped': 0,
    #     # 'start_datetime': '2019-10-18 15:18:36',
    #     # 'duration': '200s',
    #     'tbody': '''
    #                         <tr>
    #                             <td>Bill Gates</td>
    #                             <td>555 77 854</td>
    #                         </tr>
    #                                                 <tr>
    #                             <td>Bill Gates</td>
    #                             <td>555 77 854</td>
    #                         </tr>
    #                                                 <tr>
    #                             <td>Bill Gates</td>
    #                             <td>555 77 854</td>
    #                         </tr>
    #                                                 <tr>
    #                             <td>Bill Gates</td>
    #                             <td>555 77 854</td>
    #                         </tr>
    #     '''
    # }
    data = tidy_data_from_summary(summary)
    pic_path = os.path.join(settings.BASE_DIR, 'emailpic')
    pic = gen_pie_chart(data, pic_path)
    mail(task_name, receivers, pic, data)
    logger.info("邮件发送成功")

if __name__ == '__main__':
    # EnvInfo 因为使用此对象，所以本地运行不能调用，如要调试需要注释相关语句
    summary = {"success":False,"stat":{"testsRun":1,"failures":1,"errors":0,"skipped":0,"expectedFailures":0,"unexpectedSuccesses":0,"successes":0},"time":{"start_at":1571618556.609,"duration":9.371000051498413,"start_datetime":"2019-10-21 08:42:36"},"platform":{"httprunner_version":"1.5.8","python_version":"CPython 3.7.3","platform":"Windows-7-6.1.7601-SP1"},"details":[{"success":False,"stat":{"testsRun":1,"failures":1,"errors":0,"skipped":0,"expectedFailures":0,"unexpectedSuccesses":0,"successes":0},"time":{"start_at":"2019-10-21 08:42:36","duration":9.371000051498413},"records":[{"name":"查天气","status":"failure","attachment":"Traceback (most recent call last):\n  File \"D:\\api-autotest\\AutoTest\\venv\\lib\\site-packages\\httprunner\\task.py\", line 27, in runTest\n    self.test_runner.run_test(self.testcase_dict)\nhttprunner.exceptions.ValidationFailure\n\nDuring handling of the above exception, another exception occurred:\n\nTraceback (most recent call last):\n  File \"D:\\api-autotest\\AutoTest\\venv\\lib\\site-packages\\httprunner\\task.py\", line 29, in runTest\n    self.fail(repr(ex))\nAssertionError: ValidationFailure()\n","meta_data":{"request":{"url":"http://api.map.baidu.com/telematics/v3/weather?location=%E6%B7%B1%E5%9C%B3","method":"GET","headers":{"User-Agent":"python-requests/2.22.0","Accept-Encoding":"gzip, deflate","Accept":"*/*","Connection":"keep-alive"},"start_timestamp":"2019-10-21 08:42:36","body":None},"response":{"status_code":200,"headers":{"Cache-Control":"max-age=86400","Content-Length":"44","Content-Type":"application/json","Date":"Mon, 21 Oct 2019 00:42:46 GMT","Expires":"Tue, 22 Oct 2019 00:42:46 GMT","Http_x_bd_logid":"474109387","Http_x_bd_logid64":"6045878580676565106","Http_x_bd_product":"map","Http_x_bd_subsys":"apimap","P3p":"CP=\" OTI DSP COR IVA OUR IND COM \"","Server":"apache","Set-Cookie":"BAIDUID=0463822BD690241B6E870D28E54F6883:FG=1; max-age=31536000; expires=Tue, 20-Oct-20 00:42:46 GMT; domain=.baidu.com; path=/; version=1"},"content_size":44,"response_time_ms":9032.0,"elapsed_ms":23.119,"encoding":None,"content":"{\"status\":101,\"message\":\"AK参数不存在\"}","content_type":"application/json","ok":True,"url":"http://api.map.baidu.com/telematics/v3/weather?location=%E6%B7%B1%E5%9C%B3","reason":"OK","cookies":{"BAIDUID":"0463822BD690241B6E870D28E54F6883:FG=1"},"text":"{\"status\":101,\"message\":\"AK参数不存在\"}","json":{"status":101,"message":"AK参数不存在"}},"validators":[{"check":"$statuscode","expect":"200","comparator":"equals","check_value":200,"check_result":"fail"}]}}],"name":"查天气","base_url":"http://api.map.baidu.com/","output":[]}]}
    receivers = ['2335715936@qq.com', '924113801@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    send_email('task_name', summary, receivers)
