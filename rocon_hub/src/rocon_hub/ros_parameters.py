#!/usr/bin/env python3
#
# License: BSD
#   https://raw.github.com/robotics-in-concert/rocon_multimaster/license/LICENSE
#

import rospy

###############################################################################
# Functions
###############################################################################


def load():
    '''
    Returns the gateway parameters from the ros param server.

     - hub_name   : string identifer for the hub, gateways use this
     - port       : port number to run the server (default: 6380)
     - zeroconf   : whether or not to zeroconf publish this hub
     - max_memory : max amount of ram allocated for this redis server
    '''
    param = {}

    param['name'] = rospy.get_param('~name', 'Gateway Hub')
    param['port'] = rospy.get_param('~port', '6380')
    param['zeroconf'] = rospy.get_param("~zeroconf", True)
    param['max_memory'] = rospy.get_param('~max_memory', '10mb')

    return param
