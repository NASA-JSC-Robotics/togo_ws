cmake_minimum_required(VERSION 3.8)
project(togo_gz)

# find dependencies
find_package(ament_cmake REQUIRED)

# install
install(
  DIRECTORY config launch urdf worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
