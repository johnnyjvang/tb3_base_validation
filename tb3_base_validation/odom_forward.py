"""
odom_forward.py

Move forward until odometry reports 1 foot (0.3048 m) of travel,
then stop and report the measured distance.
"""

import time
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry

# Test settings
TARGET_DISTANCE = 0.3048
SPEED = 0.10


class OdomForward(Node):
    def __init__(self):
        super().__init__('odom_forward')

        # Publisher for robot velocity commands
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)

        # Subscriber for odometry feedback
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_cb, 10)

        # Start and current position tracking
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None

        # Shutdown control
        self.done = False
        self.finish_time = None

        # Run the control loop at 10 Hz
        self.timer = self.create_timer(0.1, self.loop)

    def odom_cb(self, msg):
        # Read current odometry position
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        # Save the first odometry reading as the start point
        if self.start_x is None:
            self.start_x = x
            self.start_y = y
            self.get_logger().info('Captured starting position')

        self.current_x = x
        self.current_y = y

    def publish(self, x=0.0, z=0.0):
        # Publish a TwistStamped command
        msg = TwistStamped()
        msg.twist.linear.x = x
        msg.twist.angular.z = z
        self.pub.publish(msg)

    def stop_and_exit(self, message):
        # Stop the robot and mark node ready for shutdown
        self.publish()
        self.get_logger().info(message)
        self.done = True
        self.finish_time = time.time()

    def loop(self):
        # After finishing, wait briefly, then exit cleanly
        if self.done:
            if time.time() - self.finish_time > 0.5:
                self.get_logger().info('Exiting odom_forward')
                rclpy.shutdown()
            return

        # Wait until odometry has been received
        if self.start_x is None or self.current_x is None:
            return

        # Compute displacement from start point
        dist = math.sqrt(
            (self.current_x - self.start_x) ** 2 +
            (self.current_y - self.start_y) ** 2
        )

        # Keep moving until the target distance is reached
        if dist < TARGET_DISTANCE:
            self.publish(x=SPEED)
        else:
            self.stop_and_exit(f'Target reached. Distance traveled: {dist:.3f} m')


def main(args=None):
    rclpy.init(args=args)
    node = OdomForward()
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()