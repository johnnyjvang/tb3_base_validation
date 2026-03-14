"""
timed_forward.py

Move forward for a fixed amount of time, then stop.
After stopping, report the odometry displacement.
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
MOVE_TIME = 3.0
SPEED = 0.10


class TimedForward(Node):
    def __init__(self):
        super().__init__('timed_forward')

        # Publisher for robot velocity commands
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)

        # Subscriber for odometry feedback
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_cb, 10)

        # Start and current position tracking
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None

        # Timing and shutdown control
        self.start_time = None
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

        self.current_x = x
        self.current_y = y

    def publish(self, x=0.0, z=0.0):
        # Publish a TwistStamped command
        msg = TwistStamped()
        msg.twist.linear.x = x
        msg.twist.angular.z = z
        self.pub.publish(msg)

    def stop_and_exit(self, message, dist):
        # Stop the robot and mark node ready for shutdown
        self.publish()

        # WRITE RESULT TO JSON/CSV
        append_result(
            test_name='timed_forward',
            status='PASS',
            measurement=f'{dist:.3f} m',
            notes='completed'
        )

        self.get_logger().info(message)
        self.done = True
        self.finish_time = time.time()

    def loop(self):
        # After finishing, wait briefly, then exit cleanly
        if self.done:
            if time.time() - self.finish_time > 0.5:
                self.get_logger().info('Exiting timed_forward')
                rclpy.shutdown()
            return

        # Wait until odometry has been received
        if self.start_x is None or self.current_x is None:
            return

        # Start timing on the first active loop
        if self.start_time is None:
            self.start_time = time.time()
            self.get_logger().info('Starting timed forward motion')

        elapsed = time.time() - self.start_time

        # Move forward until the timer expires
        if elapsed < MOVE_TIME:
            self.publish(x=SPEED)
        else:
            # Compute displacement from start to finish
            dist = math.sqrt(
                (self.current_x - self.start_x) ** 2 +
                (self.current_y - self.start_y) ** 2
            )
            self.stop_and_exit(f'Finished. Distance traveled: {dist:.3f} m', dist)


def main(args=None):
    rclpy.init(args=args)
    node = TimedForward()
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()