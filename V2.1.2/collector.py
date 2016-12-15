#!/bin/bash
# coding=utf-8
#
# program: Used to auto collect rally test html report
# create rally_test_result_{date}.xls and summary_{date}.html in {report_dir/{date}}
# and send email
#
# author: superhin
# date: 2016-12-7

import os
import sys
import re
import datetime
import xlwt
import ConfigParser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header


class Collector(object):

    def __init__(self):
        # html report info
        self.server = '15.15.15.12'
        self.slave = '10.100.211.204'
        self.executor = 'superhin'
        self.concurrency = '-'
        self.times = '-'

        self.task_info = 'rally_run.info'
        info = ConfigParser.ConfigParser()
        info.read(self.task_info)

        self.report_date = info.get("task_info", "date")
        self.report_dir = info.get("task_info", "report_dir")
        self.start_time = info.get("task_info", "start_time")
        self.duration = info.get("task_info", "full_duration")
        self.total_num = info.get("task_info", "total")
        self.pass_num = info.get("task_info", "pass")
        self.fail_num = info.get("task_info", "fail")

        self.report_file = self.report_dir + "/results_" + self.report_date + ".xls"
        self.html_report = self.report_dir + '/summary_' + self.report_date + '.htm'

    def collect(self):
        """
        collect rally test html report and
        create results_{date}.xls and summary_{date}.html in {report_dir}
        """

        # excel report
        wbook = xlwt.Workbook()
        wsheet = wbook.add_sheet(self.report_date)

        # excel style
        style_none = xlwt.easyxf("")
        style_head = xlwt.easyxf("font: bold 1;pattern: pattern solid, fore_colour ice_blue;")
        style_error = xlwt.easyxf("font: bold 1;pattern: pattern solid, fore_colour yellow;")
        style = style_none

        # excel col width
        wsheet.col(0).width = 10 * 367
        wsheet.col(1).width = 30 * 367
        wsheet.col(2).width = 10 * 367
        wsheet.col(3).width = 10 * 367
        wsheet.col(4).width = 10 * 367
        wsheet.col(5).width = 10 * 367
        wsheet.col(6).width = 50 * 367

        # excel head
        wsheet.write(0, 0, "Path", style_head)
        wsheet.write(0, 1, "Case", style_head)
        wsheet.write(0, 2, "Concurrency", style_head)
        wsheet.write(0, 3, "Times", style_head)
        wsheet.write(0, 4, "Success Rate", style_head)
        wsheet.write(0, 5, "Full Duration(s)", style_head)
        wsheet.write(0, 6, "Error Message", style_head)


        # html report template
        html = '''
            <!DOCTYPE html PUBLIC "-//W3C//DtdXHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            <title>Rally task results</title>
            <style>
            div {font-family: Tahoma, Geneva, sans-serif;color:#666}
            .header { text-align:left; background:#333; font-size:18px; padding:3px 20px; margin-bottom:20px; color:#fff;}
            .overview table{font-size:12px;background:#ccc;border-collapse:collapse;}
            .overview td{border:1px solid #fff;padding:0 5px}
            .detail table{font-size:12px;border-collapse:collapse;}
            .detail td{border:1px solid #ccc;padding:0 5px}
            .blue {font-style: italic;color: #03C;}
            .table_head {background-color: #69F;}
            .table_head table{font-size:12px;border-collapse:collapse;}
            .table_head td{border:1px solid #ccc;padding:0 5px}
            </style>
            </head>
            <body>
            <div class="header">
            <span>Rally task results</span></div>
            <div><h3> Task Overview</h3></div>
            <div class='overview'><table width="100%">
             <tr>
              <td height="20px"><strong>Server: </strong><span class="blue">{{server}}</span></td>
              <td><strong>Slave:</strong> <span class="blue">{{slave}}</span></td>
              <td><strong>Executor: </strong><span class="blue">{{executor}}</span></td>
              <td><strong>Concurrency: </strong><span class="blue">{{concurrency}}</span></td>
              <td><strong>Times: </strong><span class="blue">{{times}}</span></td>
             </tr>
             <tr>
              <td height="20px"><strong>Start Time: </strong><span class="blue">{{start_time}}</span></td>
              <td><strong>Duration: </strong><span class="blue">{{duration}}</span></td>
              <td><strong>Total:</strong> <span class="blue">{{total}}</span></td>
              <td><strong>Pass:</strong> <span class="blue">{{pass}}</span></td>
              <td><strong>Fail:</strong> <span class="blue">{{fail}}</span></td>
              </tr></table>
            </div>
            <div><h3> Detail Results</h3></div>
            <div class='detail'>
            <table width="100%" height="20px"><tr bgcolor="#ccc">
            <td height="20px"><strong>Case</strong></td>
            <td><strong>Concurrency</strong></td>
            <td><strong>Times</strong></td>
            <td><strong>Success_Rate</strong></td>
            <td><strong>Full_Duration(s)</strong></td>
            <td><strong>Error_Message</strong></td>
            </tr>
            {{case_details}}
            </table>
            </div>
            <p></p>
            <br/>
            </body>
            </html>
        '''

        # create html report head
        html = html.replace('{{server}}', self.server)
        html = html.replace('{{slave}}', self.slave)
        html = html.replace('{{executor}}', self.executor)
        html = html.replace('{{concurrency}}', self.concurrency)
        html = html.replace('{{times}}', self.times)
        html = html.replace('{{start_time}}', self.start_time)
        html = html.replace('{{duration}}', self.duration)
        html = html.replace('{{total}}', self.total_num)
        html = html.replace('{{pass}}', self.pass_num)
        html = html.replace('{{fail}}', self.fail_num)

        # walk report dir
        count = 0
        case_details = ''
        for path, dirs, filelist in os.walk(self.report_dir):
            for filename in filelist:
                if filename[-4:] == "html":
                    count += 1
                    fullname = os.path.join(path, filename)

                    # reg patterns
                    fd_reg = r'\"full_duration\":.(\d+).\d+,'
                    ic_reg = r'"iterations_count":.(\d*),'
                    er_reg = r'"errors",.(\d+)\]'
                    ms_reg = r'"type":."(.*?",."message":.".*?)\\n.*?",'
                    id_reg = r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}'
                    cc_reg = r'concurrency.{3,4}(\d+),'

                    fd_reg_c = re.compile(fd_reg)
                    ic_reg_c = re.compile(ic_reg)
                    er_reg_c = re.compile(er_reg)
                    ms_reg_c = re.compile(ms_reg)
                    id_reg_c = re.compile(id_reg)
                    cc_reg_c = re.compile(cc_reg)

                    # get reg patterns values in rally html report file
                    with open(fullname, 'r') as f:
                        report_html = f.read()

                        fd_report = re.findall(fd_reg_c, report_html)
                        ic_report = re.findall(ic_reg_c, report_html)
                        er_report = re.findall(er_reg_c, report_html)
                        ms_report = re.findall(ms_reg_c, report_html)
                        cc_report = re.findall(cc_reg_c, report_html)

                    full_duration = ''
                    iterations_count = ''
                    errors = ''
                    error_messages = ''
                    success_rate = ''
                    concurrency = ''

                    if fd_report:
                        full_duration = fd_report[-1]
                        iterations_count = ic_report[-1]
                        errors = er_report[-1]
                        concurrency = cc_report[-1]

                        if iterations_count != '0':
                            success_rate = str((int(iterations_count) - int(errors)) * 100 / int(iterations_count))\
                                           + '%'
                        else:
                            success_rate = '-'

                        # get error message
                        error_messages = ''
                        if ms_report:
                            error_list = []
                            for error_message in ms_report:
                                error_message = error_message.replace('", "message": "', ':')
                                duplicate = False
                                error_count = 1
                                for cur_error_message in error_list:
                                    if error_message[:30] == cur_error_message[:30]:
                                        duplicate = True
                                        error_count += 1
                                        break
                                    else:
                                        duplicate = False
                                if not duplicate:
                                    error_list.append(error_message)
                            for error_message in error_list:
                                error_messages = error_messages + error_message
                                error_messages += '\n'

                            error_messages = error_messages[:-2]
                        else:
                            error_messages = ''

                    else:
                        print 'No data'

                    # print results
                    print filename[:-5],
                    print 'full_duration: %s' % full_duration,
                    print 'concurrency: %s' % concurrency,
                    print 'iterations_count: %s' % iterations_count,
                    print 'errors: %s' % errors,
                    print 'success_rate: %s' % success_rate

                    # write excel
                    if success_rate != "100%":
                        style = style_error
                    else:
                        style = style_none

                    wsheet.write(count, 0, fullname, style)
                    wsheet.write(count, 1, filename[:-5], style)
                    wsheet.write(count, 2, concurrency, style)
                    wsheet.write(count, 3, iterations_count, style)
                    wsheet.write(count, 4, success_rate, style)
                    wsheet.write(count, 5, full_duration, style)
                    wsheet.write(count, 6, error_messages, style)

                    # create html report
                    case_details = '<tr><td>' + filename[:-5] + '</td>' + \
                                   '<td>' + concurrency + '</td>' + \
                                   '<td>' + iterations_count + '</td>' + \
                                   '<td>' + success_rate + '</td>' + \
                                   '<td>' + full_duration + '</td>' + \
                                   '<td>' + error_messages + '</td></tr>'

                    pos = html.find("{{case_details}}")
                    html = html[:pos] + case_details + html[pos:]
        wbook.save(self.report_file)
        html = html.replace('{{case_details}}', '')
        with open(self.html_report, 'w') as f2:
            f2.write(html)
        print "----------------------------------------------------------------------------"
        print "Total Cases: %d" % count

    def send_email(self):
        # email config info
        smtpserver = 'smtp.sina.com'
        user = 'test_results@sina.com'
        password = 'hanzhichao123'

        sender = 'test_results@sina.com'
        receiver = 'zhangzz6@lenovo.com'
        receiver2 = 'superhin@126.com'
        subject = 'Rally test results'

        # new a msg object
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = Header(subject, 'utf-8')
        f = open(self.html_report)
        content = f.read()
        f.close()
        text = MIMEText(content, 'html', 'utf-8')
        msg.attach(text)

        # upload attachments
        att_file = MIMEApplication(open(self.report_file, 'rb').read())
        att_file.add_header('Content-Disposition', 'attachment', filename='results_' + self.report_date + '.xls')
        msg.attach(att_file)

        # send email
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver)
        smtp.login(user, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.sendmail(sender, receiver2, msg.as_string())

        print "----------------------------------------------------------------------------"
        print "Email send done!!!"
        print "----------------------------------------------------------------------------"
        smtp.quit()

collector = Collector()
collector.collect()
collector.send_email()
