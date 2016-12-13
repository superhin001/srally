#coding:utf-8
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header

#发送邮箱服务器
smtpserver = 'smtp.sina.com'
#发送邮箱用户/密码
user = 'iivex@sina.com'
password = 'hanzhichao123'

#发送邮箱
sender = 'iivex@sina.com'

#接收邮箱
receiver = 'superhin@126.com'

#发送邮件主题
subject = 'Rally test result'

#邮件对象
msg = MIMEMultipart()
#msg = MIMEMultipart('alternative')
msg['From'] = sender
msg['To'] = receiver
msg['Subject'] = Header('Rally Test Result','utf-8')

#编写HTML类型的邮件正文
text = MIMEText('<h1>Rally Test Result<h1>','html','utf-8')
msg.attach(text)
#print msg

#添加附件

att_file = MIMEApplication(open('result.xls','rb').read())
att_file.add_header('Content-Disposition','attachment',filename='result.xls')
msg.attach(att_file)

#连接发送邮件
smtp = smtplib.SMTP()
smtp.connect(smtpserver)
smtp.login(user,password)

smtp.sendmail(sender,receiver,msg.as_string())

print "Email send done!!!"
smtp.quit()
