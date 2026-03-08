#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
import threading
import time

from geometry_msgs.msg import Point, Quaternion
from gazebo_msgs.srv import SpawnEntity, DeleteEntity, SetModelState
from gazebo_msgs.msg import ModelStates
from std_srvs.srv import Empty

from lynxmotion_al5d_description.srv import SpawnBrick, KillBrick
from lynxmotion_al5d_description.msg import Pose as BrickPoseMsg

class Brick:
    def __init__(self, node, color, name, x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0):
        self.node = node
        self.color = color
        self.name = name
        self.pose = BrickPoseMsg()
        self.pose.position = Point(x=x, y=y, z=z)
        from .utils import quaternion_from_rpy
        self.pose.orientation.roll = roll
        self.pose.orientation.pitch = pitch
        self.pose.orientation.yaw = yaw
        
        # Create publisher for brick pose
        self.pose_pub = self.node.create_publisher(
            BrickPoseMsg,
            f'/lynxmotion_al5d/{name}/pose',
            10
        )
        
        # Timer for periodic publishing
        self.timer = self.node.create_timer(0.1, self.publish_pose)
        
        self.node.get_logger().info(f"Created brick: {name} ({color}) at position ({x}, {y}, {z})")
    
    def publish_pose(self):
        self.pose_pub.publish(self.pose)
    
    def destroy(self):
        self.node.destroy_publisher(self.pose_pub)
        self.node.destroy_timer(self.timer)

class BrickManager(Node):
    def __init__(self):
        super().__init__('brick_manager')
        
        self.bricks = {}
        self.brick_count = 0
        
        # Services
        self.spawn_srv = self.create_service(
            SpawnBrick,
            '/lynxmotion_al5d/spawn_brick',
            self.spawn_brick_callback
        )
        
        self.kill_srv = self.create_service(
            KillBrick,
            '/lynxmotion_al5d/kill_brick',
            self.kill_brick_callback
        )
        
        self.clear_srv = self.create_service(
            Empty,
            '/lynxmotion_al5d/clear',
            self.clear_callback
        )
        
        self.reset_srv = self.create_service(
            Empty,
            '/lynxmotion_al5d/reset',
            self.reset_callback
        )
        
        # Gazebo service clients
        self.spawn_entity_client = self.create_client(SpawnEntity, '/spawn_entity')
        self.delete_entity_client = self.create_client(DeleteEntity, '/delete_entity')
        self.set_model_state_client = self.create_client(SetModelState, '/set_model_state')
        
        while not self.spawn_entity_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Gazebo spawn service not available, waiting...')
        
        self.get_logger().info('Brick management service loaded!')
    
    def spawn_brick_callback(self, request, response):
        color = request.color
        name = request.name if request.name else f"brick_{self.brick_count}"
        pose = request.pose
        
        # Create brick object
        brick = Brick(
            self,
            color,
            name,
            pose.position.x,
            pose.position.y,
            pose.position.z,
            pose.orientation.roll,
            pose.orientation.pitch,
            pose.orientation.yaw
        )
        
        # Spawn in Gazebo
        spawn_request = SpawnEntity.Request()
        spawn_request.name = name
        spawn_request.xml = self._get_brick_sdf(color)
        spawn_request.robot_namespace = name
        spawn_request.initial_pose.position = pose.position
        from .utils import quaternion_from_rpy
        spawn_request.initial_pose.orientation = quaternion_from_rpy(
            pose.orientation.roll,
            pose.orientation.pitch,
            pose.orientation.yaw
        )
        
        future = self.spawn_entity_client.call_async(spawn_request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None and future.result().success:
            self.bricks[name] = brick
            self.brick_count += 1
            response.name = name
            self.get_logger().info(f"Spawned brick: {name}")
        else:
            response.name = ""
            self.get_logger().error(f"Failed to spawn brick: {name}")
        
        return response
    
    def kill_brick_callback(self, request, response):
        name = request.name
        
        if name in self.bricks:
            # Delete from Gazebo
            delete_request = DeleteEntity.Request()
            delete_request.name = name
            
            future = self.delete_entity_client.call_async(delete_request)
            rclpy.spin_until_future_complete(self, future)
            
            if future.result() is not None and future.result().success:
                # Destroy brick object
                self.bricks[name].destroy()
                del self.bricks[name]
                response.result = True
                response.message = f"Successfully killed brick: {name}"
                self.get_logger().info(f"Killed brick: {name}")
            else:
                response.result = False
                response.message = f"Failed to delete brick from Gazebo: {name}"
        else:
            response.result = False
            response.message = f"Brick not found: {name}"
        
        return response
    
    def clear_callback(self, request, response):
        for name in list(self.bricks.keys()):
            delete_request = DeleteEntity.Request()
            delete_request.name = name
            
            future = self.delete_entity_client.call_async(delete_request)
            rclpy.spin_until_future_complete(self, future)
            
            if future.result() is not None and future.result().success:
                self.bricks[name].destroy()
                del self.bricks[name]
        
        self.get_logger().info("Cleared all bricks")
        return response
    
    def reset_callback(self, request, response):
        self.clear_callback(request, response)
        self.brick_count = 0
        self.get_logger().info("Reset brick system")
        return response
    
    def _get_brick_sdf(self, color):
        # Return SDF for different colored bricks
        brick_sdf = f"""<?xml version='1.0'?>
        <sdf version='1.6'>
          <model name='lego_brick'>
            <static>false</static>
            <pose>0 0 0.02 0 0 0</pose>
            <link name='link'>
              <pose>0 0 0 0 0 0</pose>
              <inertial>
                <mass>0.01</mass>
                <inertia>
                  <ixx>3.5e-6</ixx>
                  <ixy>0</ixy>
                  <ixz>0</ixz>
                  <iyy>3.5e-6</iyy>
                  <iyz>0</iyz>
                  <izz>3.5e-6</izz>
                </inertia>
              </inertial>
              <collision name='collision'>
                <geometry>
                  <box>
                    <size>0.031 0.031 0.0096</size>
                  </box>
                </geometry>
              </collision>
              <visual name='visual'>
                <geometry>
                  <box>
                    <size>0.031 0.031 0.0096</size>
                  </box>
                </geometry>
                <material>
                  <ambient>{color} 1</ambient>
                  <diffuse>{color} 1</diffuse>
                  <specular>0.1 0.1 0.1 1</specular>
                </material>
              </visual>
            </link>
          </model>
        </sdf>"""
        
        return brick_sdf
    
    def destroy(self):
        for brick in self.bricks.values():
            brick.destroy()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = BrickManager()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy()
        rclpy.shutdown()

if __name__ == '__main__':
    main()