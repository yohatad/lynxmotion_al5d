#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import (IncludeLaunchDescription, ExecuteProcess,
                             RegisterEventHandler, TimerAction, SetEnvironmentVariable)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('lynxmotion_al5d_description')

    robot_description = {
        'robot_description': Command(['xacro ', os.path.join(pkg_path, 'urdf', 'lynxmotion_al5d.urdf.xacro')])
    }

    # Disable online model database to prevent gzserver from blocking on internet access
    disable_model_db = SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', '')

    # Fix RTShaderSystem / resource path for Gazebo GUI
    set_gazebo_resource_path = SetEnvironmentVariable(
        'GAZEBO_RESOURCE_PATH',
        '/usr/share/gazebo-11'
    )

    # Allow Gazebo to resolve model://lynxmotion_al5d_description/meshes/...
    set_gazebo_model_path = SetEnvironmentVariable(
        'GAZEBO_MODEL_PATH',
        os.path.dirname(pkg_path)
    )

    # Allow Gazebo to find the mimic joint plugin
    set_gazebo_plugin_path = SetEnvironmentVariable(
        'GAZEBO_PLUGIN_PATH',
        os.path.expanduser('~/lynx_ws/install/roboticsgroup_upatras_gazebo_plugins/lib')
    )

    cleanup_gazebo = ExecuteProcess(
        cmd=['bash', '-c',
             'killall -9 gzserver 2>/dev/null; killall -9 gzclient 2>/dev/null; sleep 2; true'],
        output='screen'
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare('gazebo_ros'), 'launch', 'gazebo.launch.py'])
        ]),
        launch_arguments={
            'gui': LaunchConfiguration('gui', default='true'),
            'verbose': 'true',
            'world': LaunchConfiguration('world_name',
                                         default=os.path.join(pkg_path, 'worlds', 'al5d.world')),
        }.items()
    )

    table_description = {
        'robot_description': Command(['xacro ', os.path.join(pkg_path, 'urdf', 'table.xacro')])
    }

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    table_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='table_state_publisher',
        output='screen',
        parameters=[table_description, {'use_sim_time': True}],
        remappings=[('/robot_description', '/table_description')]
    )

    spawn_table = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'table', '-topic', '/table_description',
                   '-x', '0', '-y', '0', '-z', '0', '-timeout', '60'],
        output='screen'
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'lynxmotion_al5d', '-topic', 'robot_description',
                   '-x', '0', '-y', '0', '-z', '0.56', '-timeout', '60'],
        output='screen'
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '-c', '/controller_manager'],
        output='screen'
    )

    joint_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joints_positions', '-c', '/controller_manager'],
        output='screen'
    )

    brick_manager = Node(
        package='lynxmotion_al5d_description',
        executable='brick_manager',
        name='brick_manager',
        output='screen'
    )

    return LaunchDescription([
        disable_model_db,
        set_gazebo_resource_path,
        set_gazebo_model_path,
        set_gazebo_plugin_path,
        cleanup_gazebo,

        RegisterEventHandler(OnProcessExit(
            target_action=cleanup_gazebo,
            on_exit=[
                gazebo,
                robot_state_publisher,
                table_state_publisher,
                brick_manager,
                TimerAction(period=10.0, actions=[spawn_table, spawn_entity]),
            ]
        )),

        RegisterEventHandler(OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner]
        )),

        RegisterEventHandler(OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[joint_position_controller_spawner]
        )),
    ])
