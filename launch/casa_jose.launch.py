"""Escenario Casa de José: Gazebo Harmonic (mundo) y RViz2 (mapa 2D) en un solo arranque.

    ros2 launch launch/casa_jose.launch.py                  # desde la carpeta del repositorio
    ros2 launch socialtech_casa_jose casa_jose.launch.py    # tras colcon build (paquete instalado)

Argumentos: gui (ventana de Gazebo), rviz, map (mapa mostrado en RViz2), world, tf_map (TF estática world -> map).
No lanza ningún robot: cada equipo inserta el suyo (ver README, "Añadir un robot").
"""
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument, ExecuteProcess,
                            IncludeLaunchDescription, TimerAction)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node

ROOT = Path(__file__).resolve().parent.parent      # carpeta del repositorio o share/<paquete>


def generate_launch_description():
    gui, rviz, world, mapa = (LaunchConfiguration(n) for n in ('gui', 'rviz', 'world', 'map'))
    # Solo el NOMBRE del mundo: gz lo busca en GZ_SIM_RESOURCE_PATH (que incluye worlds/). Una ruta completa con espacios se partiría en gz_args.
    gz_args = PythonExpression(["'-r ' + ('' if '", gui, "' == 'true' else '-s ') + '", world, "'"])
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(Path(get_package_share_directory('ros_gz_sim')) / 'launch' / 'gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args, 'on_exit_shutdown': 'true'}.items())
    map_server = Node(package='nav2_map_server', executable='map_server', name='map_server', output='screen',
                      parameters=[{'yaml_filename': PathJoinSubstitution([str(ROOT / 'maps'), [mapa, '.yaml']])}],
                      condition=IfCondition(rviz))
    activar_mapa = TimerAction(period=3.0, condition=IfCondition(rviz), actions=[
        ExecuteProcess(cmd=['ros2', 'run', 'nav2_util', 'lifecycle_bringup', 'map_server'], output='screen')])
    rviz2 = Node(package='rviz2', executable='rviz2', name='rviz2', arguments=['-d', str(ROOT / 'rviz' / 'casa_jose.rviz')],
                 output='screen', condition=IfCondition(rviz))
    # TF estática identidad world -> map: el mapa 2D y el mundo de Gazebo comparten coordenadas. Sin ella RViz2 avisa de que 'map' no existe
    # mientras no haya robot. No interfiere con un localizador (publica map -> odom). Desactivar con tf_map:=false si el robot ya publica 'map'.
    tf_map = Node(package='tf2_ros', executable='static_transform_publisher', name='world_to_map',
                  arguments=['--frame-id', 'world', '--child-frame-id', 'map'], condition=IfCondition(LaunchConfiguration('tf_map')))
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true', choices=['true', 'false'], description='Ventana de Gazebo (false: solo servidor)'),
        DeclareLaunchArgument('rviz', default_value='true', choices=['true', 'false'], description='RViz2 con el mapa 2D'),
        DeclareLaunchArgument('world', default_value='casa_jose.sdf', description='Mundo de worlds/'),
        DeclareLaunchArgument('map', default_value='casa_jose', choices=['casa_jose', 'casa_jose_solo_muros', 'casa_jose_zonas_prohibidas'],
                              description='Mapa de maps/ mostrado en RViz2'),
        DeclareLaunchArgument('tf_map', default_value='true', choices=['true', 'false'], description='TF estática world -> map (identidad)'),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', str(ROOT / 'models')),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', str(ROOT / 'worlds')),
        gazebo, map_server, activar_mapa, rviz2, tf_map,      # cerrar Gazebo cierra todo (on_exit_shutdown); cerrar RViz2 no cierra Gazebo
    ])
