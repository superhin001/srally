#!/bin/bash
#coding:utf-8
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
import datetime
import ConfigParser

global INFO_FILE
global CONF_FILE
global report_dir
global today
global report_file


CONF_FILE = '../conf/default.conf'

try:
    report_dir = sys.argv[1]
except IndexError:
    report_dir='./report/'
    
today=datetime.date.today().strftime("%Y%m%d")
report_file=report_dir + "report_" + today + ".xls"
html_report=report_dir + 'rally_test_summary_' + today +'.htm'

def send_email():
    conf=ConfigParser.ConfigParser()
    conf.read(CONF_FILE)

    smtpserver = conf.get("email","smtpserver")
    user = conf.get("email","user")
    password = conf.get("email","password")

    sender = conf.get("email","sender")
    receiver = conf.get("email","receiver")


    #邮件对象
    msg = MIMEMultipart()
    #msg = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = Header('Rally test results','utf-8')
    f=open(html_report)
    content = f.read()
    f.close()
    text = MIMEText(content,'html','utf-8')
    msg.attach(text)
    #print msg

    #添加附件

    att_file = MIMEApplication(open(report_file,'rb').read())
    att_file.add_header('Content-Disposition','attachment',filename='rally_test_results_'+today+'.xls')
    msg.attach(att_file)

    #连接发送邮件
    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(user,password)

    smtp.sendmail(sender,receiver,msg.as_string())
    print "----------------------------------------------------------------------------"
    print "Email send done!!!"
    print "----------------------------------------------------------------------------"
    smtp.quit()

send_email()
