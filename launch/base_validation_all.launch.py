"""
base_validation_all.launch.py

Runs TurtleBot3 base validation tests sequentially.
"""

# Core ROS2 launch description container
from launch import LaunchDescription

# Used to trigger actions when a process exits and add delays
from launch.actions import RegisterEventHandler, TimerAction

# Event handler for detecting node shutdown
from launch.event_handlers import OnProcessExit

# ROS2 node launcher
from launch_ros.actions import Node


def generate_launch_description():

    # Test 1: timed forward motion
    timed_forward = Node(package='tb3_base_validation', executable='timed_forward', output='screen')

    # Test 2: timed backward motion
    timed_back = Node(package='tb3_base_validation', executable='timed_back', output='screen')

    # Test 3: forward motion using odometry distance
    odom_forward = Node(package='tb3_base_validation', executable='odom_forward', output='screen')

    # Test 4: backward motion using odometry distance
    odom_back = Node(package='tb3_base_validation', executable='odom_back', output='screen')

    # Test 5: rotate 90° counter-clockwise
    rotate_ccw = Node(package='tb3_base_validation', executable='rotate_ccw', output='screen')

    # Test 6: rotate 90° clockwise
    rotate_cw = Node(package='tb3_base_validation', executable='rotate_cw', output='screen')

    return LaunchDescription([

        # Start first test immediately
        timed_forward,

        # When timed_forward exits, start timed_back
        RegisterEventHandler(
            OnProcessExit(target_action=timed_forward,
                on_exit=[TimerAction(period=1.0, actions=[timed_back])])
        ),

        # When timed_back exits, start odom_forward
        RegisterEventHandler(
            OnProcessExit(target_action=timed_back,
                on_exit=[TimerAction(period=1.0, actions=[odom_forward])])
        ),

        # When odom_forward exits, start odom_back
        RegisterEventHandler(
            OnProcessExit(target_action=odom_forward,
                on_exit=[TimerAction(period=1.0, actions=[odom_back])])
        ),

        # When odom_back exits, start rotate_ccw
        RegisterEventHandler(
            OnProcessExit(target_action=odom_back,
                on_exit=[TimerAction(period=1.0, actions=[rotate_ccw])])
        ),

        # When rotate_ccw exits, start rotate_cw
        RegisterEventHandler(
            OnProcessExit(target_action=rotate_ccw,
                on_exit=[TimerAction(period=1.0, actions=[rotate_cw])])
        ),

    ])