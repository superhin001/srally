#!/bin/bash
# coding=utf-8

# program: Used to auto collect rally test html report to excel file
# user: SuperHin
# date: 2016-12-1

import re
import os
import sys

try:
    t = sys.argv[1]
    c = sys.argv[2]
except IndexError:
    t = 1
    c = 1
    print 'Using default "times": 1,"concurrency": 1'
else:
    print '"times": %s,"concurrency": %s' % (t,c)
finally:
    print "-------------------------------------------------------------"

try:
    case_dir = sys.argv[1]
except IndexError:
    case_dir = './case/'

times = '"times": ' + t
concurrency = '"concurrency": ' + c

count = 0
for path,dirs,filelist in os.walk(case_dir):
    for filename in filelist:
        if filename[-4:] == "json":
            fullname = os.path.join(path,filename)
                
            count += 1
                                
            times_reg = r'\"times\":.(\d+)'
            concurrency_reg = r'"concurrency":.(\d+)'
            times_reg_c = re.compile(times_reg)
            concurrency_reg_c = re.compile(concurrency_reg)           
            
            with open(fullname,'r') as f:
                json_content = f.read()

            json_content = re.sub(times_reg_c,times,json_content)
            json_content = re.sub(concurrency_reg_c,concurrency,json_content)
            print json_content
            print "-------------------------------------------------------------"
            with open(fullname,'w') as f2:
                f2.write(json_content)

print "Total: %s" % (count)
print "Modify case done!!!"
