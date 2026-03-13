# tb3_base_validation

A ROS 2 (Jazzy) validation suite for testing TurtleBot3 base motion behavior using timed motion, odometry displacement, and rotation accuracy.

This package provides deterministic base motion tests that verify the fundamental differential drive pipeline before debugging higher-level systems such as Nav2, SLAM, or AMCL.

---

## Overview

This package contains six base validation tests:

| Test | Description |
|-----|-------------|
| `timed_forward` | Move forward for 3 seconds and measure displacement |
| `timed_back` | Move backward for 3 seconds and measure displacement |
| `odom_forward` | Move forward until odometry reports 1 foot (0.3048 m) |
| `odom_back` | Move backward until odometry reports 1 foot |
| `rotate_ccw` | Rotate counter-clockwise until ~90° |
| `rotate_cw` | Rotate clockwise until ~90° |

All tests operate directly on:

```
/cmd_vel
/odom
```

This isolates and validates the motion pipeline:

```
cmd_vel → motor controller → wheels → encoders → odom
```

---

## Why This Matters

If the base motion system is incorrect, higher-level robotics systems will fail regardless of parameter tuning.

Affected systems include:

- Nav2
- AMCL
- SLAM
- Costmaps
- Collision Monitor

This package provides a deterministic baseline before debugging those systems.

---

## Installation

Clone into a ROS 2 workspace:

```bash
cd ~/your_ros2_ws/src
git clone https://github.com/johnnyjvang/tb3_base_validation.git
```

Build the workspace:

```bash
cd ~/your_ros2_ws
colcon build
source install/setup.bash
```

---

## Running on Real TurtleBot3

Terminal 1:

```bash
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_bringup robot.launch.py
```

Terminal 2:

```bash
cd ~/your_ros2_ws
source install/setup.bash
```

Run a single validation test:

```bash
ros2 run tb3_base_validation timed_forward
```

Run the full validation suite:

```bash
ros2 launch tb3_base_validation base_validation_all.launch.py
```

---

## Running in Simulation

Terminal 1:

```bash
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Terminal 2:

```bash
cd ~/your_ros2_ws
source install/setup.bash
```

Run a single validation test:

```bash
ros2 run tb3_base_validation odom_forward
```

Run the full validation suite:

```bash
ros2 launch tb3_base_validation base_validation_all.launch.py
```

---

## Expected Results

### Timed Motion

```
velocity = 0.10 m/s
time = 3 seconds

distance = velocity × time = 0.30 m
```

Example output:

```
Finished. Distance traveled: 0.298 m
```

Acceptable tolerance:

```
0.28 – 0.32 meters
```

### Rotation Tests

Expected output:

```
Rotation complete: 90° ± ~3°
```

---

## Diagnostic Guide

| Observation | Possible Cause |
|-------------|---------------|
| ~0.30 m | Correct encoder scaling |
| ~0.15 m | Wheel radius / encoder configuration issue |
| ~0.60 m | Encoder scaling doubled |
| Moves backward when commanded forward | Motor polarity or wheel configuration |
| Drift while moving straight | Mechanical imbalance |
| Rotation inaccurate | Angular odometry tuning |

---

## Package Structure

```
tb3_base_validation/
├── launch/
│   └── base_validation_all.launch.py
├── resource/
│   └── tb3_base_validation
├── tb3_base_validation/
│   ├── timed_forward.py
│   ├── timed_back.py
│   ├── odom_forward.py
│   ├── odom_back.py
│   ├── rotate_ccw.py
│   └── rotate_cw.py
├── package.xml
├── setup.py
└── setup.cfg
```

---

## License

Apache License 2.0
