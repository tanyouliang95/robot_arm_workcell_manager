# robot_arm_workcell_manager (RAWM)
Robot arm manipulation manager package is one of the module for the Central sterile services department (cssd) workcell application. This package will act as a standalone workcell (aka: Dispenser Robot), which handles the robotics aspect of cssd_workcell. When a `DispenserRequest` is being sent out by a user to RAWM, this workcell will begin executing the task, starting with the picking motion of custom design instrument tray from a medical rack, then end it by placing the tray on MIR cart (follow-up delivery task by MIR). Fiducial Aruco markers will function as locating visual markers for pose estimation. Aruco markers are attached to the trays and MIR cart. Current package is developed and tested on `ros-melodic` and `gazebo 9.1`. 

**STILL IN DEVELOPMENT!!!**

![alt text](/documentations/gazebo_test.png?)

*Full Video Link*, [here](https://drive.google.com/open?id=1dGKh3FVMlUwX8GUMv3mgxQFBm0OnGa8B)

---

## Getting Started

### Basic Installation

```
# ROS, Moveit stuffs
# Gazebo Stuffs
```

### Dependencies

- Universal Robot: [here](https://github.com/ros-industrial/universal_robot), **Remember to switch branch
- HanWha: TBC
- Fiducial Marker Detector: [here](https://github.com/UbiquityRobotics/fiducials)
```
sudo apt-get install ros-melodic-aruco-detect
sudo apt-get install ros-melodic-fiducial-msgs
```
- rmf_msgs: [here](https://github.com/RMFHOPE/rmf_msgs_ros1), **Phasing Out Soon
- CSSD_workcell_manager (ROS2): Work in Progress

### Make and Build
```
catkin_make --pkg cssdbot_moveit_config cssdbot_description cssd_gazebo
catkin_make --pkg robot_arm_workcell_manager -j4
```


---

## Run RAWM with Gazebo

```
# Terminal A: Run Gazebo, alongside with Rviz and Moveit
roslaunch cssd_gazebo ur10_gazebo.launch

# Terminal B: Run RAWM
roslaunch robot_arm_workcell_manager robot_arm_workcell_manager.launch
```

### Request a Task 

Open another terminal, then use rostopic to publish a `DispenserRequest.msg` to start the pick and place motion.
```
rostopic pub /cssd_workcell/dispenser_request rmf_msgs/DispenserRequest '{request_id: 0xx01, dispenser_name: ur10_001, items:[{item_type: marker_2, quantity: 1, compartment_name: 'marker_101'}] }' --once

# second request
rostopic pub /cssd_workcell/dispenser_request rmf_msgs/DispenserRequest '{request_id: 0xx02, dispenser_name: ur10_001, items:[{item_type: marker_1, quantity: 1, compartment_name: 'marker_100'}] }' --once

# third request: manually remove tray, and play with the pose of cart on gazebo
rostopic pub /cssd_workcell/dispenser_request rmf_msgs/DispenserRequest '{request_id: 0xx00, dispenser_name: ur10_001, items:[{item_type: marker_0, quantity: 1, compartment_name: 'marker_100'}] }' --once
```

By now, the robot dispenser will execute the task according to the `DispenserRequest`. GoodLuck!!

---


## Testing on submodules and lib 

### 1. Run Robot Arm Controller Test Code 
Run motion executor test code.
```
# Terminal A: Run Rviz and Robot Desciption... blablabla
roslaunch robot_arm_workcell_manager demo.launch

# Terminal B: Run arm_controller Node 
roslaunch robot_arm_workcell_manager arm_controller.launch
```

### 2. Run Fiducial Markers Handler Test Code
Test code to try out aruco marker detection. Camera and aruco markers are used for this application.

```
# Check Camera and configure path
vlc v4l2:///dev/video{$NUM}
```

**Calibration**: Refer to OpenCV Camera Calibration code, [here](https://docs.opencv.org/2.4/doc/tutorials/calib3d/camera_calibration/camera_calibration.html#results). Once done, then copy the camera & distortion matrix from a .xml file to `/robot_arm_workcell_manager/config/usb_cam.yaml`.

```
roslaunch robot_arm_workcell_manager fiducial_markers_handler.launch
```

### 3. Overall Test with Robot Arm Workcell Manager (RAWM)

This RAWM exec depends on above `robot_arm_controller` and `fiducial_markers_handler` libs. 

```
## Terminal A: Run Rviz and Moveit
roslaunch robot_arm_workcell_manager demo.launch

## Terminal B: Run RAWM
roslaunch robot_arm_workcell_manager robot_arm_workcell_manager.launch

# Terminal C: Send the same `DispenserRequest.msg` as above
```

---

## Running on hardware

1. Download [ur_modern_driver with e series](https://github.com/AdmiralWall/ur_modern_driver/tree/kinetic_ur_5_4) 
2. `roslaunch robot_arm_workcell_manager demo.launch`
3. Run script to move robot

## Notes
- A custom designed "fork-lift" end effector is used in this process
- 3 executables are used in this application, namely: `robot_arm_workcell_manager` (MAIN), `robot_arm_controller`, `fiducial_markers_handler`.
- "Named Motion Target" can be used to name then request each "joint/pose goal" of the robot arm. Edit `motion_config.yaml` accordingly.
- Camera calib is tuned, and written here: `/config/usb_cam.yaml`
- Dispenser req will be received by RAWM, id: with convention of `marker_{$fiducial_id}`
- Use Ros_bridge/SOSS to link ros1 msg to ros2, eventually communicates with a ``cssd_workcell_manager`

## Possible errors
- Error building due to gazebo::transport::node TryInit function not found
```
sudo sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list'

wget http://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -

sudo apt-get update

sudo apt-get upgrade

```

## TODO
- Code clean up!!
- gazebo model clean upssss
- robust multiple level scanning of rack
- collision model creation on the scene in moveit
- Namespace for rosparam (senario of runnin multiple robot arms)
- intergration with greater RMF environment
- Eventually, Hardware Test!!!!!!
