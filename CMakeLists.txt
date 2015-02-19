cmake_minimum_required(VERSION 2.8.3)
project(jsk_travis)
find_package(catkin REQUIRED)
catkin_package()
install(FILES rosdep-install.sh travis_jenkins.py travis.sh
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
