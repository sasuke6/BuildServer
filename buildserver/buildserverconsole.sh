#!/bin/sh

path=$(cd "$(dirname "$0")"; pwd)
export BUILD_ETC_DIR="${path}/etc"
export BUILD_LOG_DIR="${path}/logs"
export BUILD_BIN_DIR="${path}/../bin"

source ${BUILD_BIN_DIR}/environment.sh
path=$(cd "$(dirname "$0")"; pwd)


SERVICE_NAME="buildserver.py"
SERVICE="${path}/${SERVICE_NAME}"
LOG="${BUILD_LOG_DIR}/buildserver.log"
PID="${BUILD_LOG_DIR}/pid"

function Help()
{
    echo "usage: $0 [start|daemon|restart|stop|check|pause|resume]"
}

if [ $# -ne 1 ] 
then
    Help
    exit 0
fi

function Daemon()
{
    echo "start service ..."  
    echo "nohup $SERVICE > $LOG 2>&1 &"
    find $path/../bin -name "*.sh" -exec chmod a+x {} \;
    find $path/../bin -name "*py" -exec chmod a+x {} \;
    find $path -name "*py" -exec chmod a+x {} \;
#    cd $path/../bin
    nohup $SERVICE > $LOG 2>&1  & #| tee $LOG 2>&1 &
    echo $! >$PID
#    $SERVICE > $LOG 2>&1
    echo "start service finish" 
    resume
}

function Start()
{
    echo "start service ..."  
#    echo "nohup $SERVICE > $LOG 2>&1 &"
    find $path/../bin -name "*.sh" -exec chmod a+x {} \;
    find $path/../bin -name "*py" -exec chmod a+x {} \;
    find $path -name "*py" -exec chmod a+x {} \;
    #cd $path/../bin
    resume
    $SERVICE > $LOG 2>&1 | tee $LOG
}


function pause()
{
    echo "service pause"
    CURRENT_PATH="$path"
    touch ${CURRENT_PATH}/pause.flag
}

function resume()
{
    echo "service resume"
    CURRENT_PATH="$path"
    rm -f ${CURRENT_PATH}/pause.flag
}


function Stop()
{
    echo "stop service ..."  
    if [ -f $PID ]
    then
	pid=`cat $PID`
	echo "pid is $pid , kill it"
	kill $pid
	rm $PID
#    else
	#echo "kill all process named ${SERVICE_NAME}"
	#ps -ef | grep ${SERVICE_NAME} | grep python | awk '{system("kill "$2)}'
    fi
    echo "stop service finish" 
}

function Check()
{
    echo "check service ..."  
    #ps -ef | grep ${SERVICE_NAME} | grep python | grep -v grep 
    #count=`ps -ef | grep ${SERVICE_NAME} | grep python | grep -v grep | wc -l`
    ps -ef | grep python | grep 18797 | grep -v grep  
    count=`ps -ef | grep python | grep 18797 | grep -v grep | wc -l `
    echo "process count is $count"
    if [ $count -gt 0 ]
    then
        echo "service is alive"
    else
        echo "service is died"
        Start
    fi

    echo "check service finish" 
}

case $1 in
    start)
        Start
        ;;
    stop)
        Stop
        ;;
    pause)
        pause
        ;;
    resume)
        resume
        ;;
    restart)
        Stop
        sleep 2
        Start
        ;;
    check)
        Check
        ;;
    daemon)
	Daemon
	;;
    *)
        Help
        ;;
esac
