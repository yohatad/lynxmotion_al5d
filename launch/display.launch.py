#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('lynxmotion_al5d_description')
    xacro_file = os.path.join(pkg_path, 'urdf', 'lynxmotion_al5d.urdf.xacro')
    rviz_config_file = os.path.join(pkg_path, 'rviz', 'display.rviz')

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': Command(['xacro ', xacro_file]),
                'use_sim_time': False,
            }]
        ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_file],
            output='screen',
        ),
    ])
