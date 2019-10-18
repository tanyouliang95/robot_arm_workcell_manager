#!/usr/bin/env python
"""
============================================================
Creator: Tan You Liang
Date: Sept 2018
Description:  ROS1 MOVE IT Arm control
              Edit `motion_config`.yaml for motion control
MoveIt Class Functions:
  http://docs.ros.org/jade/api/moveit_ros_planning_interface/html/classmoveit_1_1planning__interface_1_1MoveGroup.html
============================================================
"""

import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
import tf
from math import pi
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list
from termcolor import colored

# global var
global arm_ns_
arm_ns_ = ""

##########################################################################################
## ============================== Some local Functions ===============================
###########################################################################################



# check if current state reaches goal state, check all joints is within tolerance
def check_pose(goal, actual, tolerance=0.005):
  """
  Convenience method for testing if a list of values are within a tolerance of their counterparts in another list
  @param: goal, actual    A list of floats, a Pose or a PoseStamped
  @param: tolerance       A float
  @returns: bool
  """
  all_equal = True
  if type(goal) is list:
    for index in range(len(goal)):
      # print "Compare tolerance> ", abs(actual[index] - goal[index]), tolerance
      if abs(actual[index] - goal[index]) > tolerance: # checking here
        return False

  elif type(goal) is geometry_msgs.msg.PoseStamped:
    return check_pose(goal.pose, actual.pose, tolerance)

  elif type(goal) is geometry_msgs.msg.Pose:
    return check_pose(pose_to_list(goal), pose_to_list(actual), tolerance)

  return True


# Change Quaternion pose with input delta rpy
def changeInOrientation( wpose_quaternion, delta_roll, delta_pitch, delta_yaw):
    
    if (wpose_quaternion == 0):
      qua = [0,0,0,1]
    else: 
      qua = [ wpose_quaternion.x,
              wpose_quaternion.y, 
              wpose_quaternion.z, 
              wpose_quaternion.w]

    (roll, pitch, yaw) = tf.transformations.euler_from_quaternion(qua)
    quaternion = tf.transformations.quaternion_from_euler(roll + delta_roll , pitch + delta_pitch, yaw + delta_yaw)

    wpose_quaternion.x = quaternion[0]
    wpose_quaternion.y = quaternion[1]
    wpose_quaternion.z = quaternion[2]
    wpose_quaternion.w = quaternion[3]

    return wpose_quaternion


# control arm velocity of cartesian by adding travel time betwwen each way points
def controlArmVelocity(plan, numberOfWayPoints = 1, timeFactor=1): 

  print "Number of Planned Waypoints ", numberOfWayPoints
  print "Time change factor as ", timeFactor

  for i in range(1, numberOfWayPoints):

    time = plan.joint_trajectory.points[i].time_from_start.to_sec()
    plan.joint_trajectory.points[i].time_from_start = rospy.Time.from_sec( time*timeFactor ) 
    plan.joint_trajectory.points[i].velocities = [ j/timeFactor  for j in plan.joint_trajectory.points[i].velocities ]  #divide vel with factor
    plan.joint_trajectory.points[i].accelerations = [ j/timeFactor  for j in plan.joint_trajectory.points[i].accelerations ]  #divide acc with factor

  return plan



#########################################################################################
## ============================== Arm Manipulator Class ===============================
#########################################################################################



class ArmManipulation(object):

  ## ------------------------------------- Start init -------------------------------------

  def __init__(self,  arm_ns_=""):
    super(ArmManipulation, self).__init__()

    moveit_commander.roscpp_initialize(sys.argv)
    robot = moveit_commander.RobotCommander(robot_description=arm_ns_+"/robot_description")                 # outer-level interface to the robot
    scene = moveit_commander.PlanningSceneInterface()         # world surrounding the robot: (will pub collision obj)
    group_name = "manipulator"                                # group name for ur manipulator
    group = moveit_commander.MoveGroupCommander(group_name, robot_description=arm_ns_+"robot_description", ns=arm_ns_)   # interface to one group of joints.

    ## `DisplayTrajectory`_ publisher which is used to pub trajectories for RViz to visualize:  
    display_trajectory_publisher = rospy.Publisher(arm_ns_+'/move_group/display_planned_path', moveit_msgs.msg.DisplayTrajectory, queue_size=20)

    # Misc variables
    self.box_name = "obj_box"
    self.robot = robot
    self.scene = scene
    self.group = group
    self.display_trajectory_publisher = display_trajectory_publisher
    self.planning_frame = group.get_planning_frame()
    self.eef_link = group.get_end_effector_link()
    self.group_names = robot.get_group_names()

    # # create model to prevent collision
    # self.addModelScene()
    # self.scene = scene

    ## Printing Basic Information
    print (colored(" --Reference frame: {}".format(self.planning_frame), "yellow"))
    print (colored(" --End effector: {}".format(self.eef_link), "yellow"))
    print (colored(" --Robot Groups: {}".format(self.group_names), "yellow"))
    print (colored(" --Robot current state: {}".format(robot.get_current_state()), "yellow"))


    # ## Check if Robot Base is added to scene before
    # self.base_name = "base_box"
    # is_known = self.base_name in scene.get_known_object_names()
    # print ("is base added before: {} \n".format(is_known))
    # if (is_known == True): # Check if base model is added be4
    #   scene.remove_world_object(self.base_name)
    #   scene.remove_world_object(self.box_name)
    #   rospy.sleep(0.5)



  # Adding space constraint by adding model in scene
  # TODO: create general function with arg to handle constraints from yaml
  def addModelScene(self):
    print ("Adding space constraint!")
    rospy.sleep(1.5) # crude method to ensure scene is loaded
      
    # Create a box in the planning scene at the location of the base, TODO
    box = geometry_msgs.msg.PoseStamped()
    box.header.frame_id = "base_link"
    box.pose.orientation.w = 1.0
    box.pose.position.z = -0.05
    self.scene.add_box("base_box", box, size=(0.7, 0.7, 0.1))

    box = geometry_msgs.msg.PoseStamped()
    box.header.frame_id = "base_link"
    box.pose.orientation.w = 1.0
    box.pose.position.y = -0.7
    box.pose.position.z = 0.5
    self.scene.add_box("side wall", box, size=(0.9, 0.1, 1.4))
    
    box = geometry_msgs.msg.PoseStamped()
    box.header.frame_id = "base_link"
    box.pose.orientation.w = 1.0
    box.pose.position.x = -0.7
    box.pose.position.z = 0.5
    self.scene.add_box("back_wall", box, size=(0.1, 1, 1.4))
    
    box = geometry_msgs.msg.PoseStamped()
    box.header.frame_id = "base_link"
    box.pose.orientation.w = 1.0
    box.pose.position.y = 0.7
    box.pose.position.z = 0.02
    self.scene.add_box("table", box, size=(0.9, 0.4, 0.25))
    
    box = geometry_msgs.msg.PoseStamped()
    box.header.frame_id = "base_link"
    box.pose.orientation.w = 1.0
    box.pose.position.x = 1
    box.pose.position.z = 0.05
    self.scene.add_box("AGV base", box, size=(0.8, 0.8, 0.4))

    rospy.sleep(1.5)  # crude method to ensure scene is loaded


  ## ------------------------------------- End init -------------------------------------


  ##
  ################################# goal joint and pose planners #################################
  ##

  """ 
  Joints move to Joint States 
  @Param, joint_goal: 6x1 list with 6 joints info
  @Param, time_factor: float, time factor
  @Return: bool, is it success
  """
  def go_to_joint_state(self, joint_goal, time_factor):

    state = self.robot.get_current_state()
    self.group.set_start_state(state)
    group = self.group

    # The go command can be called with joint values, poses, or without any
    # group.go(joint_goal, wait=True)
    plan = group.plan (joints = joint_goal)
    plan = controlArmVelocity(plan, numberOfWayPoints=len(plan.joint_trajectory.points), timeFactor=time_factor )

    group.execute(plan, wait=True)
    group.stop()

    current_joints = self.group.get_current_joint_values()

    return check_pose(joint_goal, current_joints, tolerance=0.03)


  """ 
  Eef Goal pose
  @Param, pose_list: 6x1 list with 6 dof info of the end effector
  @Param, time_factor: float, time factor
  @Return: bool, is it success
  """
  def go_to_pose_goal(self, pose_list, time_factor ):

    group = self.group

    pose_goal = geometry_msgs.msg.Pose()
    pose_goal.position.x = pose_list[0]
    pose_goal.position.y = pose_list[1]
    pose_goal.position.z = pose_list[2]
    pose_goal.orientation = changeInOrientation( 0, pose_list[3],   # roll
                                                    pose_list[4],   # pitch
                                                    pose_list[5] )  # yaw
    # group.set_pose_target(pose_goal)

    ## Planner to compute the plan and execute it.
    plan = group.plan (joints = pose_goal)
    plan = controlArmVelocity(plan, numberOfWayPoints=len(plan.joint_trajectory.points), timeFactor=time_factor )
    group.execute(plan, wait=True)
    group.stop()
    group.clear_pose_targets()
    current_pose = self.group.get_current_pose().pose
    
    return check_pose(pose_goal, current_pose, 0.01)



  ##
  #################################  Cartesian planners #################################
  ##

  """ 
  Plan end effector moves in cartesian space
  @Param, motion_list: , 6dof changes of the eef relative to previous pose
  @Param, time_factor: float, time factor
  @Return: plan (obj, planned trajectory), fraction (float, 1.0 means all completed)
  """
  def plan_cartesian_path(self, motion_list, time_factor):
    state = self.robot.get_current_state()
    self.group.set_start_state(state)
    wpose = self.group.get_current_pose().pose
    waypoints = []

    for motion_data in motion_list:
      wpose.position.x += motion_data[0]
      wpose.position.y += motion_data[1]
      wpose.position.z += motion_data[2]
      wpose.orientation = changeInOrientation(  wpose.orientation,
                                                motion_data[3],   # roll
                                                motion_data[4],   # pitch
                                                motion_data[5] )  # yaw
      waypoints.append(copy.deepcopy(wpose))

    (plan, fraction) = self.group.compute_cartesian_path(
                                    waypoints,   # waypoints to follow
                                    0.2,         # eef_step
                                    0.0)         # jump_threshold, 0 to disable
    
    plan = controlArmVelocity(plan, numberOfWayPoints=len(plan.joint_trajectory.points), timeFactor=time_factor )
    return plan, fraction



  # Displaying a Planned Trajectory
  def display_trajectory(self, plan):

    robot = self.robot
    display_trajectory_publisher = self.display_trajectory_publisher

    ## A `DisplayTrajectory`_ msg has two primary fields, trajectory_start and trajectory.
    ## We populate the trajectory_start with our current robot state to copy over
    ## any AttachedCollisionObjects and add our plan to the trajectory.
    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(plan)
    # Publish
    display_trajectory_publisher.publish(display_trajectory)


  
  """ 
  Execute plan paths/trajetory
  @Param, plan: planned path of the robot arm
  @Return: bool, is it success
  """
  def execute_plan(self, plan):
    state = self.robot.get_current_state()
    self.group.set_start_state(state)
    self.group.execute(plan, wait=True)
    self.group.stop() # TODO: testing
    return True


  ##
  ################################# Scene Object Handlers #################################
  ##


  # Ensuring Collision Object state Updates Are Receieved
  def wait_for_state_update(self, box_is_known=False, box_is_attached=False, timeout=4):

    box_name = self.box_name
    scene = self.scene

    start = rospy.get_time()
    seconds = rospy.get_time()

    while (seconds - start < timeout) and not rospy.is_shutdown():
      # Test if the box is in attached objects
      attached_objects = scene.get_attached_objects([box_name])
      is_attached = len(attached_objects.keys()) > 0

      # Test if the box is in the scene.
      # Note that attaching the box will remove it from known_objects
      is_known = box_name in scene.get_known_object_names()

      # Test if we are in the expected state
      if (box_is_attached == is_attached) and (box_is_known == is_known):
        return True

      # Sleep so that we give other threads time on the processor
      rospy.sleep(0.1)
      seconds = rospy.get_time()

    # If we exited the while loop without returning then we timed out
    return False


  # Adding Objects to the Planning Scene
  def add_box(self, timeout=4):

    ## Create a box in the planning scene at the location of the left finger:
    box_pose = geometry_msgs.msg.PoseStamped()
    box_pose.header.frame_id = "ee_link"
    box_pose.pose.orientation.w = 1.0
    box_name = self.box_name

    self.scene.add_box( box_name, box_pose, size=(0.1, 0.1, 0.1) )
    return self.wait_for_state_update(box_is_known=True, timeout=timeout)


  # Attaching Objects to the Robot
  def attach_box(self, timeout=4):

    box_name = self.box_name
    robot = self.robot
    scene = self.scene
    eef_link = self.eef_link
    group_names = self.group_names

    ## attach the box to the eef. Manipulating objects requires the robot be able to touch them without the planning scene
    ## reporting the contact as a collision. By adding link names to the ``touch_links`` array, planning scene will ignore 
    ## collisions between those links and the box. grasping group depends on model of robot manipulator
    grasping_group = 'manipulator'
    touch_links = robot.get_link_names(group=grasping_group)
    scene.attach_box(eef_link, box_name, touch_links=touch_links)

    # Wait for the planning scene to update.
    return self.wait_for_state_update(box_is_attached=True, box_is_known=False, timeout=timeout)


  # Detaching Objects from the Robot
  def detach_box(self, timeout=4):

    box_name = self.box_name
    scene = self.scene
    eef_link = self.eef_link
    scene.remove_attached_object(eef_link, name=box_name)
    
    # We wait for the planning scene to update.
    return self.wait_for_state_update(box_is_known=True, box_is_attached=False, timeout=timeout)


  # Removing Objects from the Planning Scene  
  def remove_box(self, timeout=4):

    box_name = self.box_name
    scene = self.scene

    scene.remove_world_object(box_name)
    ## **Note:** The object must be detached before we can remove it from the world

    # We wait for the planning scene to update.
    return self.wait_for_state_update(box_is_attached=False, box_is_known=False, timeout=timeout)

  
  """
  Get Eef pose
  @Return: position.x (.y, .z), and orientation.x (.y, .z, .w)
  if not able to get pose, will return 0 for all elements
  """
  def get_eef_pose(self):
    return self.group.get_current_pose().pose

  
  """
  Get arm joints
  @Return: Float Array of 6 joint values: [j0,j1,j2,j3,j4,j5]
  if not able to get value, will return empty array[]
  """
  def get_arm_joints(self):
    return self.group.get_current_joint_values()





if __name__ == '__main__':
  rospy.init_node('robot_manipulator_control_testing_node', anonymous=True)

  ur10 = ArmManipulation( arm_ns_ = "/arm2/" )
  print "==================== testing ============ "

  # joints_goal = [0,-2.55,2.6,-0.062,1.614,  0]
  # joints_goal = [0,-2.45,2.5,-0.062,1.614,  0]
  joints_goal = [-3.3, -0.6,1.9,-1.25,-0.3, -0.05]
  # joints_goal = [1.57, -2.1,2.15,-0.062,1.614, 0]
  print ur10.get_arm_joints()
  ur10.go_to_joint_state(joints_goal, 1)


