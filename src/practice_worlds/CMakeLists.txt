cmake_minimum_required(VERSION 3.8)
project(practice_worlds)

# find dependencies
find_package(ament_cmake REQUIRED)

# install
install(
  DIRECTORY worlds models
  DESTINATION share/${PROJECT_NAME}
)

ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/${PROJECT_NAME}.dsv.in")

ament_package()

