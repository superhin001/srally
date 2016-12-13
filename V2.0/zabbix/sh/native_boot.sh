#!/bin/bash
report_dir=/usr/local/native
report_file=${report_dir}/boot.html
check_report()
{
    if [ "$1" = "full_duration" ];then
        f=`cat $report_file | grep -o "\"full_duration\":.*,.*\"config\""`
        f=${f%.*}
        f=${f#*:}
        let r=($RANDOM%10+1)
        echo $f
else
        echo 0
    fi
}

check_report $1
