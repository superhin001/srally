#!/bin/bash
# coding=utf-8

# program: Used to auto collect rally test html report to excel file
# user: SuperHin
# date: 2016-12-1

import os
import sys
import re
import datetime
import xlwt
import ConfigParser

global TEMPLATE_FILE
global INFO_FILE
global html_report
global CONF_FILE
global report_dir
global today
global report_file
global html

today=datetime.date.today().strftime("%Y%m%d")

try:
    report_dir = sys.argv[1]
except IndexError:
    report_dir='./report/'


report_file = report_dir + "rally_test_results_" + today + ".xls"
html_report = report_dir + 'rally_test_summary_' + today + '.htm'

TEMPLATE_FILE = '../template/email_template.html'
INFO_FILE = report_dir +'/rally_run.info'
CONF_FILE = '../conf/default.conf'


def collect_report():
    count = 0

    #excel_report
    wbook=xlwt.Workbook()
    wsheet = wbook.add_sheet(today)
    style_none = xlwt.easyxf("")
    style_head = xlwt.easyxf("font: bold 1;pattern: pattern solid, fore_colour ice_blue;")
    style_error = xlwt.easyxf("font: bold 1;pattern: pattern solid, fore_colour yellow;")
    style=style_none

    wsheet.write(0, 0, "Path", style_head)
    wsheet.write(0, 1, "Case", style_head)
    wsheet.write(0, 2, "Concurrency", style_head)
    wsheet.write(0, 3, "Times", style_head)
    wsheet.write(0, 4, "Success Rate", style_head)
    wsheet.write(0, 5, "Full Duration(s)", style_head)
    wsheet.write(0, 6, "Error Message", style_head)

    #html_report
    conf = ConfigParser.ConfigParser()
    conf.read(CONF_FILE)
    server = conf.get("task","server")
    slave = conf.get("task","slave")
    executor = conf.get("task","executor")
    concurrency = conf.get("task","concurrency")
    times = conf.get("task","times")


    info = ConfigParser.ConfigParser()
    info.read(INFO_FILE)
    start_time=info.get("task_info", "start_time")
    duration=info.get("task_info", "full_duration")
    total_num=info.get("task_info", "total")
    pass_num=info.get("task_info", "pass")
    fail_num=info.get("task_info", "fail")

    with open(TEMPLATE_FILE) as f:
        html = f.read()
        #print html
        html = html.replace('{{server}}',server)
        html = html.replace('{{slave}}',slave)
        html = html.replace('{{executor}}',executor)
        html = html.replace('{{concurrency}}',concurrency)
        html = html.replace('{{times}}',times)
        html = html.replace('{{start_time}}',start_time)
        html = html.replace('{{duration}}',duration)
        html = html.replace('{{total}}',total_num)
        html = html.replace('{{pass}}',pass_num)
        html = html.replace('{{fail}}',fail_num)

    case_details = ''
    
    for path,dirs,filelist in os.walk(report_dir):
        for filename in filelist:
            if filename[-4:] == "html":
                fullname = os.path.join(path,filename)
                #fsplit = fullname.split('\\')
                #fpath =  fsplit[-3] + '/' + fsplit[-2]
                count += 1
                #print fullname
                
                fd_reg = r'\"full_duration\":.(\d+).\d+,'
                ic_reg = r'"iterations_count":.(\d*),'
                er_reg = r'"errors",.(\d+)\]'
                #ms_reg = r'("type":.".*?",."message":.".*?"),."traceback"'
                ms_reg = r'"type":."(.*?",."message":.".*?)\\n.*?",'
                id_reg = r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}'
                cc_reg = r'concurrency.{3,5}(\d+),'

                fd_reg_c = re.compile(fd_reg)
                ic_reg_c = re.compile(ic_reg)
                er_reg_c = re.compile(er_reg)
                ms_reg_c = re.compile(ms_reg)
                id_reg_c = re.compile(id_reg)
                cc_reg_c = re.compile(cc_reg)

                f = open(fullname,'r')
                report_html = f.read()

                fd_report = re.findall(fd_reg_c,report_html)
                ic_report = re.findall(ic_reg_c,report_html)
                er_report = re.findall(er_reg_c,report_html)
                ms_report = re.findall(ms_reg_c,report_html)
                cc_report = re.findall(cc_reg_c,report_html)

                f.close()
                
                full_duration=''
                iterations_count=''
                errors=''
                error_messages=''
                success_rate=''
                concurrency=''

                if fd_report != []:
                    full_duration=fd_report[-1]
                    iterations_count=ic_report[-1]
                    errors=er_report[-1]

                    concurrency=cc_report[-1]

                    if iterations_count != '0':
                        success_rate = str((int(iterations_count) - int(errors)) * 100 / int(iterations_count)) + '%'
                    else:
                        success_rate = -1

                    error_messages = ''

                    if ms_report != []:

                        error_list = []
                        for error_message in ms_report:
                            error_message = error_message.replace('", "message": "',':')
                            #print error_message
                            duplicate = False
                            for cur_error_message in error_list:
                                if error_message[:30] == cur_error_message[:30]:
                                    duplicate = True
                                    break
                                else:
                                    duplicate = False
                            if duplicate == False:
                                error_list.append(error_message)
                        #print error_list
                        for error_message in error_list:
                            #print error_message
                            #print ('\n')
                            error_messages = error_messages + error_message
                            error_messages = error_messages + '\n'
                            #print error_messages
                        error_messages = error_messages[:-2]
                    else:
                        error_messages = ''

                else:
                    print 'No data'

                print filename[:-5],
                print 'full_duration: %s' % full_duration,
                print 'concurrency: %s' % concurrency,
                print 'iterations_count: %s' % iterations_count,
                print 'errors: %s' % errors,
                print 'success_rate: %s' % success_rate

                if success_rate != "100%":
                    style = style_error
                else:
                    style = style_none
                
                wsheet.col(0).width=10*367
                wsheet.col(1).width=30*367
                wsheet.col(2).width=10*367
                wsheet.col(3).width=10*367
                wsheet.col(4).width=10*367
                wsheet.col(5).width=10*367
                wsheet.col(6).width=50*367
                
                wsheet.write(count,0,fullname, style)
                wsheet.write(count,1,filename[:-5], style)
                wsheet.write(count,2,concurrency, style)
                wsheet.write(count,3,iterations_count, style)
                wsheet.write(count,4,success_rate, style)
                wsheet.write(count,5,full_duration, style)
                wsheet.write(count,6,error_messages, style)

                #create_html_report
                case_details = case_details +\
                               '<tr><td>' + filename[:-5] + '</td>'\
                               '<td>' + concurrency + '</td>'\
                               '<td>' + iterations_count + '</td>'\
                               '<td>' + success_rate + '</td>'\
                               '<td>' + full_duration + '</td>'\
                               '<td>' + error_messages + '</td></tr>'
                              
                pos = html.find("{{case_details}}")
                html = html[:pos] + case_details + html[pos:]
                

    wbook.save(report_file)
    html = html.replace('{{case_details}}','')
    with open(html_report,'w') as f2:
        f2.write(html)
    print "----------------------------------------------------------------------------"
    print "Total Cases: %d" % count
