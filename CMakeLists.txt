cmake_minimum_required(VERSION 3.8)
project(lynxmotion_al5d_description)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)

# Generate interfaces
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RPY.msg"
  "msg/Pose.msg"
  "srv/SpawnBrick.srv"
  "srv/KillBrick.srv"
  "srv/TeleportAbsolute.srv"
  "srv/TeleportRelative.srv"
  DEPENDENCIES geometry_msgs
)

# Install launch files
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# Install URDF and meshes
install(DIRECTORY urdf
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY meshes
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY models
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY worlds
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY rviz
  DESTINATION share/${PROJECT_NAME}
)

# Install brick_manager as an executable script
install(PROGRAMS
  lynxmotion_al5d_description/brick_manager.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME brick_manager
)

# Export dependencies
ament_export_dependencies(rosidl_default_runtime)
ament_export_dependencies(geometry_msgs)
ament_export_dependencies(std_msgs)
ament_export_dependencies(std_srvs)

ament_package()