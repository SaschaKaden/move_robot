#!/usr/bin/env python

import threading
import curses

import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64
from panda import *

from move_robot.srv import *


def keyboard_input(robot, gripper):
    print("Keyboard input started")
    screen = curses.initscr()
    screen.keypad(True)

    while not rospy.is_shutdown():
        key = curses.initscr().getch()
        # print(key)
        translation_offset = 0.005
        orientation_offset = 0.005

        # Translation
        if key == curses.KEY_UP:
            robot.pose.pose.position.z += translation_offset
            print("Up")
        elif key == curses.KEY_DOWN:
            robot.pose.pose.position.z -= translation_offset
            print("Down")
        elif key == 52:  # Num 4
            robot.pose.pose.position.y += translation_offset
            print("Left")
        elif key == 54:  # Num 6
            robot.pose.pose.position.y -= translation_offset
            print("Right")
        elif key == 56:  # Num 8
            robot.pose.pose.position.x += translation_offset
            print("Forward")
        elif key == 50:  # Num 2
            robot.pose.pose.position.x -= translation_offset
            print("Backward")
        # Orientation
        elif key == 113:  # Q
            robot.pose.pose.orientation.x += orientation_offset
            print("Roll left")
        elif key == 101:  # E
            robot.pose.pose.orientation.x -= orientation_offset
            print("Roll right")
        elif key == 97:  # A
            robot.pose.pose.orientation.y += orientation_offset
            print("Pitch down")
        elif key == 100:  # D
            robot.pose.pose.orientation.y -= orientation_offset
            print("Pitch up")
        elif key == 119:  # W
            robot.pose.pose.orientation.z += orientation_offset
            print("Yaw left")
        elif key == 115:  # S
            robot.pose.pose.orientation.z -= orientation_offset
            print("Yaw right")
        # Gripper
        elif key == 99:  # C
            gripper.grasp(0.006, 0.1)
            print("Grasp")
        elif key == 111:  # O
            gripper.homing()
            print("Homing")
        elif key == 27:  # ESC
            print("Quit")
            return
        else:
            print("Not an saved key!")


if __name__ == '__main__':
    rospy.init_node('caller')
    rospy.wait_for_service('/start_joint')
    rospy.wait_for_service('/start_cart')
    rospy.wait_for_service('/start_velocity')
    rospy.wait_for_service('/stop_controller')
    print("Services found")

    # start joint controller
    start_vel_service = rospy.ServiceProxy('/start_velocity', StartController)
    response = start_vel_service(StartControllerRequest())
    rospy.sleep(1)
    gripper = Gripper()
    robotJoint = RobotJoint()

    print("move to home position")
    [joints, tcp] = load_state(path="/home/sascha/catkin_ws/data/home.json")
    robotJoint.set_target(joints)
    rospy.sleep(1)  # 3
    gripper.homing()

    print("move to grasp position")
    [joints, tcp] = load_state(path="/home/sascha/catkin_ws/data/grasp.json")
    robotJoint.set_target(joints)
    rospy.sleep(6)
    robotJoint.stop()
    rospy.sleep(0.2)
    # gripper.grasp(0.02, 0.1, 50)
    gripper.grasp(0.0075, 0.1, 50)
    rospy.sleep(0.1)

    print("move to drink position")
    [joints_drink, tcp] = load_state(
        path="/home/sascha/catkin_ws/data/drink.json")

    [joints_drink_2, tcp] = load_state(
        path="/home/sascha/catkin_ws/data/drink_2.json")

    robotJoint.set_target(joints_drink)
    rospy.sleep(4)
    robotJoint.set_target(joints_drink_2)
    rospy.sleep(2.5)
    robotJoint.set_target(joints_drink)
    rospy.sleep(2.5)
    gripper.homing()
    robotJoint.stop()
    rospy.sleep(1)

    print("stop joint controller")
    stop_controller_service = rospy.ServiceProxy(
        '/stop_controller', StopController)
    rospy.sleep(3)

    # # let the robot drink
    # # start cartesian controller
    # start_cart_service = rospy.ServiceProxy('/start_cart', StartController)
    # response = start_cart_service(StartControllerRequest())
    # rospy.sleep(5)
    # robot = RobotCart()
    # print("Robot initialized")

    # # let the user control the robot with the keyboard
    # keyThread = threading.Thread(
    #     target=keyboard_input, args=(robot, gripper,)).start()

    # rospy.spin()
