#/bin/bash

#program: to auto run rally tasks and get html reports
#user: hzc
#date:2016.8.25

if [ ! -d "report" ]; then
  mkdir report
fi

if [ ! -d "error_tasks" ]; then
  mkdir error_tasks
fi

for filename in `ls *.json`
do
	#echo $filename
	rally task start ${filename} 2>&1 | tee report/${filename%.*}.log
	reportcmd=`cat report/${filename%.*}.log | grep -m1 "rally task report" | cut -d " " -f 1-5`
	#echo $reportcmd
	if [ -z "$reportcmd" ]
	then
		echo "can't find reportcmd"
		cp $filename error_tasks/
	else
		${reportcmd} report/${filename%.*}.html
	fi
	sleep 5
done 
