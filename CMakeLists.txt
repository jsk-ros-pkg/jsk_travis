cmake_minimum_required(VERSION 2.8.3)
project(jsk_travis)
find_package(catkin REQUIRED rostest)
catkin_package()
add_rostest(test/example.test)

if(CATKIN_ENABLE_TESTING)
  # For testing ADDITIONAL_ENV_TO_DOCKER
  catkin_add_nosetests(test/test_env_var.py)
  # Check if rosdep is correctly install scipy
  if ("$ENV{ROS_DISTRO}" STRGREATER "hydro") # hydro does not install pip scipy
    catkin_add_nosetests(test/test_scipy.py)
    catkin_add_nosetests(test/test_lxml.py)
  endif()
endif()

set(ENABLE_TEST_GAZEBO OFF CACHE BOOL "Option to enable testing gazebo")
if(ENABLE_TEST_GAZEBO)
  add_rostest(test/gazebo.test)
endif()

file(GLOB_RECURSE script_files RELATIVE ${PROJECT_SOURCE_DIR} *.sh *.py)
message(STATUS "install ${script_files}")
install(FILES ${script_files}
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
