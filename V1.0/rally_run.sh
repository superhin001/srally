#/bin/bash

#program: to auto run rally tasks and get html reports
#user: hzc
#date:2016.8.25


modify_tc()
{  
    for filename in `ls *.json`
	do
        sed -i 's/"times":.*,/"times": 1,/g' $filename
        sed -i 's/"concurrency": [0-9]\{1\}/"concurrency": 1/g' $filename
	done
}

run_tasks()
{
if [ ! -d "report" ]; then
  mkdir report
fi

if [ ! -d "log" ]; then
  mkdir log
fi

if [ ! -d "error_tasks" ]; then
  mkdir error_tasks
fi

for filename in `ls *.json`
do
	echo $filename
	rally task start ${filename} 2>&1 | tee log/${filename%.*}.log
	reportcmd=`cat log/${filename%.*}.log | grep -m1 "rally task report" | cut -d " " -f 1-5`
	is_na = `cat log/${filename%.*}.log | grep 'n/a'`
	echo $reportcmd
	if [ -z "$reportcmd" ]; then
		echo "can't find reportcmd"
		cp $filename error_tasks/
	elif [ -n "$is_na" ];then
		cp $filename error_tasks/
	else
		${reportcmd} report/${filename%.*}.html
	fi
	sleep 5
done 
}

collect_result()
{
    if [ -d "report" ]; then
        python collect_result.py
	else
	    echo "report dir not exists"
    fi 
}

send_email()
{
    if [ -f "result.xls" ]; then
	    python send_email.py
	else
	    echo "result.xls not exists"
	fi
}

modify_tc
run_tasks
collect_result
send_email

