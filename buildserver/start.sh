#!/usr/bin/bash
path=$(cd "$(dirname "$0")"; pwd)
source "${path}/../bin/environment.sh"
export BUILD_ETC_DIR="${path}/etc"
export BUILD_LOG_DIR="${path}/logs"
cd $path/../bin
python  ${path}/buildserver.py 

