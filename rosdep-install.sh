#!/bin/bash -x

trap 'find -L . -name manifest.xml.deprecated | xargs -n 1 -i dirname {} | xargs -n 1 -i mv `pwd`/{}/manifest.xml.deprecated `pwd`/{}/manifest.xml' 1 2 3 15

find -L . -name package.xml -exec dirname {} \; | xargs -n 1 -i find {} -name manifest.xml | xargs -n 1 -i mv {} {}.deprecated # rename manifest.xml for rosdep install
PACKAGE_PATH_LIST=(${ROS_PACKAGE_PATH//:/\ /})
ROS_PACKAGE_PATH_REVERSED=`for ((i=${#PACKAGE_PATH_LIST[@]}-1; i>=0; i--)); do if [ -e ${PACKAGE_PATH_LIST[$i]} ]; then echo -n ${PACKAGE_PATH_LIST[$i]}' '; fi; done`
EXIT_STATUS=1
COUNT=0
while [ $EXIT_STATUS == 1 -a $COUNT -lt 3 ] ; do  # try 3 times with "Continue installing despite errors." option
    COUNT=$((COUNT + 1))
    rosdep install -q -y --rosdistro $ROS_DISTRO $ROSDEP_ADDITIONAL_OPTIONS --from-paths ${ROS_PACKAGE_PATH_REVERSED} .
    EXIT_STATUS=$?
    [ $EXIT_STATUS == 0 ] || sleep 30
done
[ $EXIT_STATUS == 0 ] || rosdep install -q -y --rosdistro $ROS_DISTRO $ROSDEP_ADDITIONAL_OPTIONS --from-paths ${ROS_PACKAGE_PATH_REVERSED} .

find -L . -name manifest.xml.deprecated | xargs -n 1 -i dirname {} | xargs -n 1 -i mv `pwd`/{}/manifest.xml.deprecated `pwd`/{}/manifest.xml

