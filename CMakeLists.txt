cmake_minimum_required(VERSION 3.8)
project(socialtech_casa_jose NONE)
find_package(ament_cmake REQUIRED)

install(DIRECTORY launch worlds models maps rviz DESTINATION share/${PROJECT_NAME})
# Añade share/<paquete>/models a GZ_SIM_RESOURCE_PATH al hacer source del workspace (model:// resuelve sin configurar nada)
ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.dsv.in")

ament_package()
