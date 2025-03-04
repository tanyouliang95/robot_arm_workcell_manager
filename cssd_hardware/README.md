
# Cssd_Hardware (RAWM)
This package is to bring up all dependent codes/packages to spawn up the hardware. (RAWM, robot arm, camera....). The test here is mainly on UR10e.  
PLEASE KEEP YOUR HANDS ON THE BIG RED BUTTON!

## Prerequisites
 * Intel Realsense, install from [here](https://github.com/IntelRealSense/realsense-ros)
 * UR Robot Driver
  * UR_modern_driver: [ur_modern_driver with e series](https://github.com/AdmiralWall/ur_modern_driver/tree/kinetic_ur_5_4), `kinectic_ur_5_4` branch
  * or, [`ur_robot_driver`](https://github.com/UniversalRobots/Universal_Robots_ROS_Driver)
    * Please refer to the README for setup, also the debug process [here](https://github.com/UniversalRobots/Universal_Robots_ROS_Driver/issues/55)


```
catkin_make --pkg cssd_hardware -j4
```

---

## Launching single UR10e arm
The Current UR10e robor IP is: `10.233.29.33`. Remember to switch the UR10e pendant to "remote" in order to control the arm via ROS. 

Then launch 'single_arm launch'. This bringup will spawn all required nodes: driver, RAWM, MoveIt, RVIZ, realsense cam:
```
roslaunch cssd_hardware single_arm.launch
```
or.... with the new `ur_robot_driver`
```
roslaunch cssd_hardware single_arm_new.launch
```

After bringup, send a `dispenserRequest` to move the arm
```bash
rostopic pub /cssd_workcell/dispenser_requests rmf_dispenser_msgs/DispenserRequest \
'{request_guid: 0xx03, target_guid: ur10e_001, items:[{type_guid: marker_1, quantity: 1, compartment_name: 'marker_102'}] }' --once
# second request
rostopic pub /cssd_workcell/dispenser_requests rmf_dispenser_msgs/DispenserRequest \
'{request_guid: 0xx03, target_guid: ur10e_001, items:[{type_guid: marker_3, quantity: 1, compartment_name: 'marker_103'}] }' --once
```

Again, PLEASE KEEP YOUR HANDS ON THE BIG RED BUTTON! :fire:


## Launching of two arms
**Not Yet Ready :frowning_man:**

- Please change launch file below to set the ip of robot, and all other parameters

```
roslaunch cssd_hardware two_arm.launch
```

---

## Launching single HanWha arm

Connect to the right IP and the copy the `hanwha_script` to the hanwha pendant. To run HanWha Arm workcell with RMF:
```bash
roslaunch robot_arm_workcell_manager hanwha_arm_workcell_manager.launch
# run rviz on a seperate terminal 
rviz -f base_link
```

Publish sample `DispenserRequest`...
```bash
rostopic pub /cssd_workcell/dispenser_requests rmf_dispenser_msgs/DispenserRequest '{request_guid: 0xx01, target_guid: hanwha_001 }' --once
```

---

## Notes

To test it with moveit on Rviz (terminal B)*

![alt text](/documentations/rviz.gif?)

```bash
# For ur10e,
roslaunch ur_modern_driver ur10e_bringup.launch robot_ip:=XXXXXXX
# Another terminal, For ur10e,
roslaunch cssdbot_ur10e_moveit_config realistic_minimal.launch
```

To purely tryout using moveit on rviz, remember:
- !!!PLAN BEFORE EXECUTING. SCALE YOUR VELOCITY!!!!
- Remember `CURRENT STATE` should always be :`<current_state>`, `GROUP` should be: `MANIPULATOR`
- Joint states can be altered in `cssdbot_urxx_moveit_config/config/urxx.srdf`
- remember to switch the `controller_action_ns` in `cssdbot_urxx_moveit_config/config/controllers.yaml` according to the type of UR driver
  ```yaml
  controller_list:
    - name: ""
      ## when running: 'ur_modern_driver'
      action_ns: follow_joint_trajectory 
      ## when running: 'ur_robot_driver'
      action_ns: scaled_pos_traj_controller/follow_joint_trajectory
  ```