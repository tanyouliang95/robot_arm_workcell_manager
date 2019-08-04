# robot_arm_workcell_manager (RAWM)
Robot arm manipulation with moveit and fiducial markers. This Robot Arm manipulation will act as a individual standalone workcell, which user can interact with it by standard `rmf_msgs`. Robot arm will execute simple pick and place, which fiducial markers will be used to locate the target object's pose. Package is developed and tested with ros-melodic. 

**PACKAGE IS STILL IN DEVELOPMENT!!!**

![alt text](/documentations/rviz_bot.png?)


## Getting Started

### Installation
```
# ROS moveit stuffs
# Robot Arm Dependencies
# Gazebo Stuffs
```

### Dependencies
- Fiducial Marker Detector: [here](https://github.com/UbiquityRobotics/fiducials)
```
sudo apt-get install ros-melodic-aruco-detect
sudo apt-get install ros-melodic-fiducial-msgs
```
- rmf_msgs: [here](null)


### Make and Build
```
catkin_make --pkg cssdbot_moveit_config cssd_ur_description   # TODO: add it xml
catkin_make --pkg robot_arm_workcell_manager -j4
```

## Run the Code

### 1. Run Robot Arm Controller Test Code
Run motion executor test code.
```
# Absolute Path
rosrun robot_arm_workcell_manager robot_arm_controller_node _motion_target_yaml_path:="/home/youliang/catkin_ws/src/robot_arm_workcell_manager/config/motion_target.yaml" _group_name:="manipulator"
## OR
roslaunch robot_arm_workcell_manager arm_controller.launch
```

### 2. Run Fiducial Markers Handler Test Code
Test code to try out aruco marker detection. Camera and aruco markers are used for this application.
```
# Check Camera and configure path
vlc v4l2:///dev/video{$NUM}
```

Run Test Code
```
roslaunch robot_arm_workcell_manager fiducial_markers_handler.launch
## or
roslaunch robot_arm_workcell_manager markers_detector.launch
rosrun robot_arm_workcell_manager fiducial_markers_handler_node _camera_frame_id:="camera" _marker_tf_path:="/home/youliang/catkin_ws/src/robot_arm_workcell_manager/config/markers_tf.yaml"
```

**Calibration**
Refer to OpenCV Camera Calibration code ([here](https://docs.opencv.org/2.4/doc/tutorials/calib3d/camera_calibration/camera_calibration.html#results)). This tool has provided a chessboard.png for calibration. Once done, then copy the camera & distortion matrix from a .xml file to `/robot_arm_workcell_manager/config/usb_cam.yaml`.


### 3. Overall Test with Robot Arm Workcell Manager (RAWM)

This RAWM exec depends on above `robot_arm_controller` and `fiducial_markers_handler` libs. 

```
## Run Rviz and Moveit
roslaunch robot_arm_workcell_manager demo.launch

## Load Param
roscd robot_arm_workcell_manager
cd config
rosparam load rawm_param.yaml

## Run Exec
rosrun robot_arm_workcell_manager robot_arm_workcell_manager
```

### 4. Gazebo Environment Testing (TODO)
```
roslaunch cssd_ur_description ur10_gazebo.launch
```

### Request a Task 

Pub a `DispenserRequest.msg` to start the pick and place motion.
```
rostopic pub /cssd_workcell/dispenser_request rmf_msgs/DispenserRequest '{request_id: test_reqeust, dispenser_name: ur10_001, items:[{item_type: marker_0, quantity: 1, compartment_name: 'marker_100'}] }' --once
```

While the task is ongoing, user can check state of the arm_workcell by rostopic echo `/dispenser_state` and `dispenser_result` topic. 


## Notes
- A custom designed "fork-lift" end effector is used in this process
- 3 executables are used in this application, namely: `robot_arm_workcell_manager` (MAIN), `robot_arm_controller`, `fiducial_markers_handler`.
- "Named Motion Target" can be used to name then request each "joint/pose goal" of the robot arm. Edit `motion_config.yaml` accordingly.
- Camera calib is tuned, and written here: `/config/usb_cam.yaml`
- Dispenser req will be received by RAWM, id: with convention of `marker_{$fiducial_id}`
- Use Ros_bridge to link ros1 msg to ros2

## TODO
- Namespace for rosparam (senario of runnin multiple robot arms)
- Fix camera frame between `camera_optical_frame` and `camera`  (and update new tf tree)
- config for `robot_arm_workcell_manager` exec
- cmake list exec for `robot_arm_controller` and `fiducial_markers_handler`
- Gazebo simulation