#!/bin/bash

git clone http://github.com/jsk-ros-pkg/euslisp-docs ~/euslisp-docs
for pkg in ~/ros/ws_$REPOSITORY_NAME/build/*; do
    cd $pkg;
    if ls *.md > /dev/null 2>&1; then
        name=`basename $pkg`;
        echo $name;
        ls -al *.md
        mkdir -p ~/euslisp-docs/docs/$name/
        cp *.md ~/euslisp-docs/docs/$name/
        git add ~/euslisp-docs/docs/$name/*.md
        git commit -m "update documentation for $name" -a
    fi
done
