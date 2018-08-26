#!/bin/bash
#
#    Modified: Sunday, August 26, 2018 11:04 AM
#
cwd=`pwd`
cd ${HOME}/File-Sherpa
source app/bin/activate
python3 app/file_sherpa.py $@
cd ${cwd}
