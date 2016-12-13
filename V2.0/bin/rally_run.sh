#/bin/bash
run_tasks()
{
export today=`date +%Y%m%d`
export report_dir=report/${today}
export error_dir=report/${today}/error_tasks
export start_time=`date '+%Y-%m-%d %H:%M:%S'`


if [ ! -d "report" ]; then
    mkdir report
fi
mkdir $report_dir
mkdir $error_dir
echo "----------------------------------------------------------------------------"
echo "Rally Test Start"
echo "----------------------------------------------------------------------------"
total=`ls *.json | wc -l`
for filename in `ls *.json`
do
    pass=0
    fail=0
    echo $filename
    echo "----------------------------------------------------------------------------"
	rally task start ${filename} 2>&1 | tee ${report_dir}/${filename%.*}.log
	reportcmd=`cat ${report_dir}/${filename%.*}.log | grep -m1 "rally task report" | cut -d " " -f 1-5`
	is_na = `cat ${report_dir}/${filename%.*}.log | grep 'n/a'` 2>/dev/null
	echo $reportcmd
	if [ -z "$reportcmd" ] || [ -n "$is_na" ]; then
        let "fail=fail+1"
		echo "can't find reportcmd"
		cp $filename ${error_dir}/
        cp ${report_dir}/${filename%.*}.log ${error_dir}/
	else
        let "pass=pass+1"
		${reportcmd} ${report_dir}/${filename%.*}.html
	fi
	sleep 5
done 
export end_time=`date '+%Y-%m-%d %H:%M:%S'`
start_stamp=`date -d "$end_time" +%s`
end_stamp=`date -d "$start_time" +%s`
let duration_time=($end_stamp-$start_stamp)
let duration_h=($duration_time/3600)
let duration_m=($duration_time%3600/60)
let duration_s=($duration_time%60)
echo "----------------------------------------------------------------------------"
echo "Start Time: ${start_time}    End Time: ${end_time}"
echo "Full Duration: ${duration_h} h  ${duration_m} m  ${duration_s} s"
echo "----------------------------------------------------------------------------"

echo "[task_info]" >>rally_run.info
echo "date={today}" >>rally_run.info
echo "report_dir=${report_dir}" >>rally_run.info
echo "start_time=${start_time}" >>rally_run.info
echo "end_time=${end_time}" >>rally_run.info
echo "full_duration=${duration_h}h${duration_m}m${duration_s}s" >>rally_run.info
echo "total=${total}" >>rally_run.info
echo "pass=${pass}" >>rally_run.info
echo "fail=${fail}" >>rally_run.info

}
run_tasks


