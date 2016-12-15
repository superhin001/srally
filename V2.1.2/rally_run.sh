#/bin/bash
source profile
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/home/kevin/rally/bin'
cd /root/hzc/20161209

run_tasks()
{
now=`date +%Y%m%d_%H%M%S`
report_dir=report/${now}
error_dir=report/${now}/error_tasks
start_time=`date '+%Y-%m-%d %H:%M:%S'`

if [ ! -d "report" ]; then
    mkdir report
fi
mkdir -p $report_dir
mkdir -p $error_dir
echo "----------------------------------------------------------------------------"
echo "Rally Test Start"
echo "----------------------------------------------------------------------------"
total=`ls *.json | wc -l`
export pass=0
export fail=0
for filename in `ls *.json`
do
    echo $filename
    echo "----------------------------------------------------------------------------"
	rally task start ${filename} 2>&1 | tee ${report_dir}/${filename%.*}.log
	reportcmd=`cat ${report_dir}/${filename%.*}.log | grep -m1 "rally task report" | cut -d " " -f 1-5`
	is_na = `cat ${report_dir}/${filename%.*}.log | grep 'n/a'` 2>/dev/null
	echo $reportcmd
	if [ -z "$reportcmd" ] || [ -n "$is_na" ]; then
        fail=`expr $fail + 1`
		echo "can't find reportcmd"
		cp $filename ${error_dir}/
        cp ${report_dir}/${filename%.*}.log ${error_dir}/
	else
        pass=`expr $pass+1`
		${reportcmd} ${report_dir}/${filename%.*}.html
	fi
	sleep 5
done 
end_time=`date '+%Y-%m-%d %H:%M:%S'`
start_stamp=`date -d "$start_time" +%s`
end_stamp=`date -d "$end_time" +%s`
let "duration_time=(end_stamp-start_stamp)"
let "duration_h=(duration_time/3600)"
let "duration_m=(duration_time%3600/60)"
let "duration_s=(duration_time%60)"
echo "----------------------------------------------------------------------------"
echo "Start Time: ${start_time}    End Time: ${end_time}"
echo "Full Duration: ${duration_h} h  ${duration_m} m  ${duration_s} s"
echo "----------------------------------------------------------------------------"

echo "[task_info]" >rally_run.info
echo "date=${now}" >>rally_run.info
echo "report_dir=${report_dir}" >>rally_run.info
echo "start_time=${start_time}" >>rally_run.info
echo "end_time=${end_time}" >>rally_run.info
echo "full_duration=${duration_h}h${duration_m}m${duration_s}s" >>rally_run.info
echo "total=${total}" >>rally_run.info
echo "pass=${pass}" >>rally_run.info
echo "fail=${fail}" >>rally_run.info
cp rally_run.info ${report_dir}/
}
run_tasks
python collector.py

