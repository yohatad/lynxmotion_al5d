# Lynxmotion AL5D Description - ROS2 Migration

This package has been successfully migrated from ROS to ROS2 (Humble). The migration includes all essential functionality with proper ROS2 interfaces and launch system.

## Package Overview

Provides URDF/Xacro description of Lynxmotion AL5D robot arm, Gazebo integration, brick management services, and visualization tools.

## Installation

### Prerequisites

1. ROS2 Humble (installed)
2. Additional ROS2 packages for full functionality:

```bash
# Install Gazebo ROS integration (required for simulation)
sudo apt install ros-humble-gazebo-ros ros-humble-gazebo-msgs ros-humble-gazebo-ros-pkgs

# Install controller packages
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers
```

### Building the Package

```bash
cd /home/yoha/lynx/ros2_ws
colcon build --packages-select lynxmotion_al5d_description
source install/setup.bash
```

## Launch Files

### 1. Visualization Only (No Gazebo Required)
```bash
ros2 launch lynxmotion_al5d_description display.launch.py
```
- Requires: `rviz2`, `robot_state_publisher`, `joint_state_publisher_gui`
- Provides: Robot visualization in RViz with joint control GUI

### 2. World Visualization with Table
```bash
ros2 launch lynxmotion_al5d_description world.launch.py
```
- Requires: Same as display launch plus table model
- Provides: Robot and table visualization

### 3. Gazebo Simulation (Requires Gazebo ROS)
```bash
ros2 launch lynxmotion_al5d_description al5d_gazebo_control.launch.py
```
- **Requires:** Gazebo ROS packages installed (see Prerequisites)
- Provides: Full Gazebo simulation with controllers and brick management

## Services

The package provides the following ROS2 services for brick management:

- `/lynxmotion_al5d/spawn_brick` - Spawn a colored brick in Gazebo
- `/lynxmotion_al5d/kill_brick` - Remove a brick from Gazebo
- `/lynxmotion_al5d/clear` - Clear all bricks
- `/lynxmotion_al5d/reset` - Reset brick system

## Messages

- `lynxmotion_al5d_description/msg/Pose` - Custom pose with RPY orientation
- `lynxmotion_al5d_description/msg/RPY` - Roll, Pitch, Yaw representation

## Migration Notes

### Key Changes from ROS to ROS2:
1. **Launch Files**: Converted from XML to Python launch files
2. **Build System**: Changed from catkin to ament_cmake
3. **Python Nodes**: Updated to use rclpy instead of rospy
4. **Parameter Handling**: Uses ROS2 parameter system
5. **Service Interfaces**: ROS2 service definitions with proper namespacing

### Fixed Issues:
1. RViz configuration updated for ROS2 plugin naming (`rviz_default_plugins/` instead of `rviz/`)
2. Proper dependency management in package.xml
3. Python entry points defined in setup.py

## Testing

Verify the migration:
```bash
# Check available interfaces
ros2 interface list | grep lynx

# Test message definition
ros2 interface show lynxmotion_al5d_description/msg/Pose

# Test visualization (works without Gazebo)
ros2 launch lynxmotion_al5d_description display.launch.py
```

## Troubleshooting

### Gazebo ROS Not Found Error
If you encounter `package 'gazebo_ros' not found`, install the required packages:
```bash
sudo apt install ros-humble-gazebo-ros ros-humble-gazebo-msgs
```

### RViz Plugin Errors
The RViz configuration has been updated for ROS2. If you still see plugin errors, check that `rviz_default_plugins` is installed.

### Controller Issues
For Gazebo simulation with controllers, ensure `ros2_control` and `ros2_controllers` are installed.

## File Structure

```
lynxmotion_al5d_description/
├── launch/                    # ROS2 Python launch files
│   ├── display.launch.py     # RViz visualization
│   ├── world.launch.py       # World with table
│   └── al5d_gazebo_control.launch.py  # Gazebo simulation
├── msg/                      # Custom messages
│   ├── Pose.msg
│   └── RPY.msg
├── srv/                      # Custom services
│   ├── SpawnBrick.srv
│   ├── KillBrick.srv
│   ├── TeleportAbsolute.srv
│   └── TeleportRelative.srv
├── urdf/                     # URDF/Xacro files
├── config/                   # Configuration files
├── models/                   # Gazebo models
├── worlds/                   # Gazebo worlds
├── rviz/                     # RViz configurations
├── meshes/                   # Mesh files
└── lynxmotion_al5d_description/  # Python package
    ├── brick_manager.py      # Brick management node
    └── utils.py              # Utility functions
```

The migration is complete and ready for use with ROS2 Humble.