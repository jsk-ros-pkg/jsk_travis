cmake_minimum_required(VERSION 2.8.3)
project(jsk_travis)
find_package(catkin REQUIRED rostest)
catkin_package()
add_rostest(test/example.test)

if(CATKIN_ENABLE_TESTING)
  # For testing ADDITIONAL_ENV_TO_DOCKER
  catkin_add_nosetests(test/test_env_var.py)
endif()

set(ENABLE_TEST_GAZEBO OFF CACHE BOOL "Option to enable testing gazebo")
if(ENABLE_TEST_GAZEBO)
  add_rostest(test/gazebo.test)
endif()

install(FILES rosdep-install.sh travis_jenkins.py travis.sh
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
