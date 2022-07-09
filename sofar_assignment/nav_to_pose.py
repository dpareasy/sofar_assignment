#! /usr/bin/env python3
# Copyright 2021 Samsung Research America
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#from socket import RDS_CMSG_RDMA_UPDATE
import time
import os
import sys
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
import rclpy
from rclpy.node import Node
from threading import Thread
from keepout_zones.robot_navigator import BasicNavigator, NavigationResult
from rclpy.executors import MultiThreadedExecutor
'''
Basic navigation demo to go to pose.
'''

def SetX():
    while True:
        try:
            X = float(input("Please enter the X coordinate: "))
        except ValueError:
            print("Invalid input")
            continue
        else:
            break
    return X
            
def SetY():
    while True:
        try:
            Y = float(input("Please enter the Y coordinate: "))
        except ValueError:
            print("Invalid input")
            continue
        else:
            break
    return Y

class MoveTiago(Node):
    def __init__(self):
        super().__init__('nav_to_pose_demo')
        self.navigator = BasicNavigator()

        self.initial_pose = PoseStamped()
        self.initial_pose.header.frame_id = 'map'
        self.initial_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        self.initial_pose.pose.position.x = -1.5
        self.initial_pose.pose.position.y = 1.0
        self.initial_pose.pose.orientation.z = 0.0
        self.initial_pose.pose.orientation.w = 0.1

        self.navigator.setInitialPose(self.initial_pose)
    def move_to_goal(self,x,y):
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.orientation.w = 1.0

        self.navigator.goToPose(goal_pose)

        i = 0
        while not self.navigator.isNavComplete():
            # Do something with the feedback
            i = i + 1
            feedback = self.navigator.getFeedback()
            if feedback and i % 5 == 0:
                print('Estimated time of arrival: ' + '{0:.0f}'.format(
                    Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9)
                    + ' seconds.')

                # Some navigation timeout to demo cancellation
                if Duration.from_msg(feedback.navigation_time) > Duration(seconds = 600.0):
                    self.navigator.cancelNav()

                # Some navigation request change to demo preemption
                #if Duration.from_msg(feedback.navigation_time) > Duration(seconds=18.0):
                #    goal_pose.pose.position.x = -3.0
                #    navigator.goToPose(goal_pose)

        # Do something depending on the return code
        result = self.navigator.getResult()
        if result == NavigationResult.SUCCEEDED:
            print('Goal succeeded!')
        elif result == NavigationResult.CANCELED:
            print('Goal was canceled!')
        elif result == NavigationResult.FAILED:
            print('Goal failed!')
        else:
            print('Goal has an invalid return status!')


def main(args=None):
    rclpy.init(args=args)
    controller = MoveTiago()

    while rclpy.ok():

        try:
           
            x = SetX()
            y = SetY()

            controller.move_to_goal(x,y)

            print("\n---------------\n")

        except KeyboardInterrupt:
            print('\nClient Killed')
            try:
                controller.destroy_node()
                rclpy.shutdown()
                sys.exit(0)
            except SystemExit:
                os._exit(1)



if __name__ == '__main__':
    main()
