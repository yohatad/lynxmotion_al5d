#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('lynxmotion_al5d_description')

    robot_xacro_file = os.path.join(pkg_path, 'urdf', 'lynxmotion_al5d.urdf.xacro')
    table_xacro_file = os.path.join(pkg_path, 'urdf', 'table.xacro')

    robot_description = {'robot_description': Command(['xacro ', robot_xacro_file])}
    table_description = {'robot_description': Command(['xacro ', table_xacro_file])}

    # Robot joint state publisher GUI (interactive sliders for the robot's joints)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # Table state publisher
    table_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='table_state_publisher',
        output='screen',
        parameters=[table_description],
        remappings=[('/robot_description', '/table_description')]
    )

    # map → world (robot base frame)
    al5d_wrt_map_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='al5d_wrt_map_tf',
        arguments=['--x', '0', '--y', '0', '--z', '0.54',
                   '--roll', '0', '--pitch', '0', '--yaw', '0',
                   '--frame-id', 'map', '--child-frame-id', 'world']
    )

    # map → table_link
    table_wrt_map_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='table_wrt_map_tf',
        arguments=['--x', '0', '--y', '0', '--z', '0',
                   '--roll', '0', '--pitch', '0', '--yaw', '0',
                   '--frame-id', 'map', '--child-frame-id', 'table_link']
    )

    rviz_config_file = os.path.join(pkg_path, 'rviz', 'display.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        table_state_publisher,
        joint_state_publisher_gui,
        al5d_wrt_map_tf,
        table_wrt_map_tf,
        rviz,
    ])
