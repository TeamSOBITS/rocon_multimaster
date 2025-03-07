#!/usr/bin/env python3
#       
# License: BSD
#   https://raw.github.com/robotics-in-concert/rocon_multimaster/hydro-devel/rocon_gateway_tests/LICENSE 
#
##############################################################################
# Imports
##############################################################################

import rospy
import rocon_gateway
import sys

##############################################################################
# Main
##############################################################################

if __name__ == '__main__':
    rospy.init_node('pull_all')
    cancel_flag = rospy.get_param("cancel", False)
    try:
        rocon_gateway.samples.pull_all(cancel=cancel_flag)
    except rocon_gateway.GatewaySampleRuntimeError as e:
        rospy.logerr("Pull All: %s" % str(e))
        sys.exit(1)
