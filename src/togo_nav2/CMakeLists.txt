cmake_minimum_required(VERSION 3.8)
project(togo_nav2)

# find dependencies
find_package(ament_cmake REQUIRED)

# install
install(
  DIRECTORY config launch rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
