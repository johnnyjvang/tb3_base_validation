from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'tb3_base_validation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jvang',
    maintainer_email='johnnyjvang@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'timed_forward = tb3_base_validation.timed_forward:main',
            'timed_back = tb3_base_validation.timed_back:main',

            'odom_forward = tb3_base_validation.odom_forward:main',
            'odom_back = tb3_base_validation.odom_back:main',

            'rotate_ccw = tb3_base_validation.rotate_ccw:main',
            'rotate_cw = tb3_base_validation.rotate_cw:main',
        ],
    },
)
