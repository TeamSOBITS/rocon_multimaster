#!/usr/bin/env python3
#
# License: BSD
#   https://raw.github.com/robotics-in-concert/rocon_multimaster/hydro_devel/rocon_gateway_tests/LICENSE
#
##############################################################################
# Imports
##############################################################################

import rospy
import sys
import rocon_console.console as console
from rocon_gateway import samples
from rocon_gateway import GatewaySampleRuntimeError
from rocon_gateway import Graph
from rocon_gateway import GatewayError
import unittest
import rosunit


##############################################################################
# Main
##############################################################################

class TestPulls(unittest.TestCase):

    def setUp(self):
        print("\n********************************************************************")
        print("* Pull Tests Setup")
        print("********************************************************************")
        rospy.init_node('test_pulls')
        self.graph = Graph()

    def test_pull_all(self):
        print("\n********************************************************************")
        print("* Pull All")
        print("********************************************************************")
        try:
            samples.pull_all()
        except GatewaySampleRuntimeError as e:
            self.fail("Runtime error caught when advertising all connections.")
        pulled_interface = self._wait_for_pulled_interface()
        rospy.loginfo(console.cyan + "  - local gateway graph : \n%s" % self.graph._local_gateway + console.reset)
        self.assertEquals("5", str(len(pulled_interface)))

        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/add_two_ints" and remote_rule.rule.node.split(',')[0] == "/add_two_ints_server" and remote_rule.rule.type == "service"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/chatter" and remote_rule.rule.node.split(',')[0] == "/talker" and remote_rule.rule.type == "publisher"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/chatter" and remote_rule.rule.node.split(',')[0] == "/listener" and remote_rule.rule.type == "subscriber"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/fibonacci/server" and remote_rule.rule.node.split(',')[0] == "/fibonacci_server" and remote_rule.rule.type == "action_server"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/fibonacci/client" and remote_rule.rule.node.split(',')[0] == "/fibonacci_client" and remote_rule.rule.type == "action_client"]), 1)

        # Revert state
        try:
            samples.pull_all(cancel=True)
        except GatewaySampleRuntimeError as e:
            self.fail("Runtime error caught when unadvertising all connections.")
        self._assert_cleared_pulled_interface()

    def test_pull_tutorials(self):
        print("\n********************************************************************")
        print("* Pull Tutorials")
        print("********************************************************************")
        try:
            samples.pull_tutorials()
        except GatewaySampleRuntimeError as e:
            self.fail("Runtime error caught when advertising tutorial connections.")
        pulled_interface = self._wait_for_pulled_interface()
        rospy.loginfo(console.cyan + "  - local gateway graph : \n%s" % self.graph._local_gateway + console.reset)
        self.assertEquals("5", str(len(pulled_interface)))

        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/add_two_ints" and remote_rule.rule.node.split(',')[0] == "/add_two_ints_server" and remote_rule.rule.type == "service"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/chatter" and remote_rule.rule.node.split(',')[0] == "/talker" and remote_rule.rule.type == "publisher"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/chatter" and remote_rule.rule.node.split(',')[0] == "/listener" and remote_rule.rule.type == "subscriber"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/fibonacci/server" and remote_rule.rule.node.split(',')[0] == "/fibonacci_server" and remote_rule.rule.type == "action_server"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/fibonacci/client" and remote_rule.rule.node.split(',')[0] == "/fibonacci_client" and remote_rule.rule.type == "action_client"]), 1)

        try:
            samples.pull_tutorials(cancel=True)
        except GatewaySampleRuntimeError as e:
            self.fail("Runtime error caught when unadvertising tutorial connections.")
        self._assert_cleared_pulled_interface()

    def test_pull_regex_tutorials(self):
        print("\n********************************************************************")
        print("* Pull Regex Tutorials")
        print("********************************************************************")
        try:
            samples.pull_tutorials(regex_patterns=True)
        except GatewaySampleRuntimeError as e:
            self.fail("Runtime error caught when advertising tutorial connections.")
        pulled_interface = self._wait_for_pulled_interface()
        rospy.loginfo(console.cyan + "  - local gateway graph : \n%s" % self.graph._local_gateway + console.reset)
        self.assertEquals("5", str(len(pulled_interface)))

        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/add_two_ints" and remote_rule.rule.node.split(',')[0] == "/add_two_ints_server" and remote_rule.rule.type == "service"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/chatter" and remote_rule.rule.node.split(',')[0] == "/talker" and remote_rule.rule.type == "publisher"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/chatter" and remote_rule.rule.node.split(',')[0] == "/listener" and remote_rule.rule.type == "subscriber"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/fibonacci/server" and remote_rule.rule.node.split(',')[0] == "/fibonacci_server" and remote_rule.rule.type == "action_server"]), 1)
        self.assertEquals(len([remote_rule for remote_rule in pulled_interface if remote_rule.rule.name == "/fibonacci/client" and remote_rule.rule.node.split(',')[0] == "/fibonacci_client" and remote_rule.rule.type == "action_client"]), 1)

        try:
            samples.pull_tutorials(cancel=True, regex_patterns=True)
        except GatewaySampleRuntimeError as e:
            self.fail("Runtime error caught when unadvertising tutorial connections.")
        self._assert_cleared_pulled_interface()

    def tearDown(self):
        pass

    ##########################################################################
    # Utility methods
    ##########################################################################

    def _wait_for_pulled_interface(self):
        pulled_interface = None
        while not pulled_interface:
            self.graph.update()
            pulled_interface = self.graph._local_gateway.pulled_connections
            rospy.sleep(1.0)
        return pulled_interface

    def _assert_cleared_pulled_interface(self):
        start_time = rospy.Time.now()
        while True:
            self.graph.update()
            pulled_interface = self.graph._local_gateway.pulled_connections
            if not pulled_interface:
                result = "cleared"
                break
            else:
                rospy.sleep(0.2)
            if rospy.Time.now() - start_time > rospy.Duration(2.0):
                result = "timed out waiting for pulled interface to clear"
                break
        self.assertEqual("cleared", result)

NAME = 'test_pulls'
if __name__ == '__main__':
    rosunit.unitrun('test_pulls', NAME, TestPulls, sys.argv, coverage_packages=['rocon_gateway'])

