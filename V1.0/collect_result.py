# coding=utf-8

# program: Used to auto collect rally test html result to excel file
# user: SuperHin
# date: 2016-10-18

import os
import re
import xlwt

basepath = 'report/'
count = 0

wbook=xlwt.Workbook()
wsheet = wbook.add_sheet("Sheet1")
styple = xlwt.easyxf("font: bold 1")

            
wsheet.write(0,0,"Path")
wsheet.write(0,1,"Case")
wsheet.write(0,2,"Concurrency")
wsheet.write(0,3,"Times")
wsheet.write(0,4,"Success Rate")
wsheet.write(0,5,"Full Duration(s)")
wsheet.write(0,6,"Error Message")
print "------------------------------------------------------------------"
for path,dirs,filelist in os.walk(basepath):
    for filename in filelist:
        if filename[-4:] == "html":
            fullname = os.path.join(path,filename)
            #fsplit = fullname.split('\\')
            #fpath =  fsplit[-3] + '/' + fsplit[-2]
            count += 1
            #print fullname
            f = open(fullname,'r')
            html = f.read()
            
            fd_reg = r'\"full_duration\":.(\d+).\d+,'
            ic_reg = r'"iterations_count":.(\d*),'
            er_reg = r'"errors",.(\d+)\]'
            #ms_reg = r'("type":.".*?",."message":.".*?"),."traceback"'
            ms_reg = r'"type":."(.*?",."message":.".*?)\\n.*?",."traceback"'
            id_reg = r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}'
            cc_reg = r'concurrency.{3,5}(\d+),'
            
            fd_reg_c = re.compile(fd_reg)
            ic_reg_c = re.compile(ic_reg)
            er_reg_c = re.compile(er_reg)
            ms_reg_c = re.compile(ms_reg)
            id_reg_c = re.compile(id_reg)
            cc_reg_c = re.compile(cc_reg)
            
            fd_result = re.findall(fd_reg_c,html)
            ic_result = re.findall(ic_reg_c,html)
            er_result = re.findall(er_reg_c,html)
            ms_result = re.findall(ms_reg_c,html)
            cc_result = re.findall(cc_reg_c,html)

            full_duration=''
            iterations_count=''
            errors=''
            error_messages=''
            success_rate=''
            concurrency=''
            
            if fd_result != []:
                full_duration=fd_result[-1]
                iterations_count=ic_result[-1]    
                errors=er_result[-1]
                
                concurrency=cc_result[-1]
                
                if iterations_count != '0':
                    success_rate = str((int(iterations_count) - int(errors)) * 100 / int(iterations_count)) + '%'
                else:
                    success_rate = -1
                    
                error_messages = ''
                
                if ms_result != []:
                    
                    error_list = []
                    for error_message in ms_result:
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

            #print fpath,
            print filename[:-5],   
                    
            print 'full_duration: %s' % full_duration,
            print 'concurrency: %s' % concurrency,
            print 'iterations_count: %s' % iterations_count,
            print 'errors: %s' % errors,
            print 'success_rate: %s' % success_rate
            #print 'error messages: %s' % error_messages

            wsheet.col(0).width=10*367
            wsheet.col(1).width=30*367
            wsheet.col(2).width=10*367
            wsheet.col(3).width=10*367
            wsheet.col(4).width=10*367
            wsheet.col(5).width=10*367
            wsheet.col(6).width=50*367
            
            wsheet.write(count,0,fullname)
            wsheet.write(count,1,filename[:-5])
            wsheet.write(count,2,concurrency)
            wsheet.write(count,3,iterations_count)
            wsheet.write(count,4,success_rate)
            wsheet.write(count,5,full_duration)
            wsheet.write(count,6,error_messages)

            f.close()
wbook.save("./result.xls")
print "------------------------------------------------------------------"
print count
print "------------------------------------------------------------------"

