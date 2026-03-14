"""
rotate_ccw.py

Rotate the robot 90 degrees counter-clockwise using odometry yaw.
"""

import time
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry

# ADD THIS IMPORT
from tb3_base_validation.result_utils import append_result

# Test settings
TARGET_ANGLE_DEG = 90.0
ANGULAR_SPEED = 0.5


def normalize_angle(angle):
    # Keep angle in [-pi, pi] to avoid wraparound issues
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


class RotateCCW(Node):
    def __init__(self):
        super().__init__('rotate_ccw')

        # Publisher for robot velocity commands
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)

        # Subscriber for odometry feedback
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_cb, 10)

        # Start and current yaw tracking
        self.start_yaw = None
        self.current_yaw = None

        # Shutdown control
        self.done = False
        self.finish_time = None

        # Run the control loop at 10 Hz
        self.timer = self.create_timer(0.1, self.loop)

    def odom_cb(self, msg):
        # Convert quaternion orientation into yaw
        q = msg.pose.pose.orientation
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        # Save first yaw reading as the rotation start point
        if self.start_yaw is None:
            self.start_yaw = yaw

        self.current_yaw = yaw

    def publish(self, x=0.0, z=0.0):
        # Publish a TwistStamped command
        msg = TwistStamped()
        msg.twist.linear.x = x
        msg.twist.angular.z = z
        self.pub.publish(msg)

    def stop_and_exit(self, message, delta_deg):
        # Stop the robot and mark node ready for shutdown
        self.publish()

        # WRITE RESULT TO JSON/CSV
        append_result(
            test_name='rotate_ccw',
            status='PASS',
            measurement=f'{delta_deg:.1f} deg',
            notes='rotation complete'
        )

        self.get_logger().info(message)
        self.done = True
        self.finish_time = time.time()

    def loop(self):
        # After finishing, wait briefly, then exit cleanly
        if self.done:
            if time.time() - self.finish_time > 0.5:
                self.get_logger().info('Exiting rotate_ccw')
                rclpy.shutdown()
            return

        # Wait until yaw has been initialized
        if self.start_yaw is None or self.current_yaw is None:
            return

        # Compute yaw change from start
        delta = normalize_angle(self.current_yaw - self.start_yaw)
        delta_deg = math.degrees(delta)

        # Rotate until the target angle is reached
        if abs(delta_deg) < TARGET_ANGLE_DEG:
            self.publish(z=ANGULAR_SPEED)
        else:
            self.stop_and_exit(
                f'Rotation complete. Rotated: {delta_deg:.1f} deg',
                delta_deg
            )


def main(args=None):
    rclpy.init(args=args)
    node = RotateCCW()
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()