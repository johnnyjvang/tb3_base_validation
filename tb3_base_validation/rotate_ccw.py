import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry


TARGET_ANGLE_DEG = 90.0
ANGULAR_SPEED = 0.5


def normalize_angle(angle):
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


class RotateAngle(Node):
    def __init__(self):
        super().__init__('rotate_angle')

        self.cmd_pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.start_yaw = None
        self.current_yaw = None
        self.finished = False

        self.target_angle_rad = math.radians(TARGET_ANGLE_DEG)
        self.timer = self.create_timer(0.1, self.control_loop)

    def odom_callback(self, msg: Odometry):
        q = msg.pose.pose.orientation
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        if self.start_yaw is None:
            self.start_yaw = yaw
            self.get_logger().info('Captured starting yaw')

        self.current_yaw = yaw

    def publish_cmd(self, linear_x: float = 0.0, angular_z: float = 0.0):
        msg = TwistStamped()
        msg.twist.linear.x = linear_x
        msg.twist.angular.z = angular_z
        self.cmd_pub.publish(msg)

    def control_loop(self):
        if self.start_yaw is None or self.current_yaw is None:
            return

        delta = normalize_angle(self.current_yaw - self.start_yaw)

        if abs(delta) < self.target_angle_rad:
            self.publish_cmd(angular_z=ANGULAR_SPEED)
        elif not self.finished:
            self.publish_cmd(0.0, 0.0)
            self.get_logger().info(
                f'Rotation complete. Rotated: {math.degrees(delta):.1f} deg'
            )
            self.finished = True


def main(args=None):
    rclpy.init(args=args)
    node = RotateAngle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()