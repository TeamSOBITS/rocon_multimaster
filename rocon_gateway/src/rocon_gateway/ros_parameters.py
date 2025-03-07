#!/usr/bin/env python3
#
# License: BSD
#   https://raw.github.com/robotics-in-concert/rocon_multimaster/license/LICENSE
#

import os.path
import re

import rosparam
import rospy
from gateway_msgs.msg import Rule, RemoteRule

from . import utils

###############################################################################
# Functions
###############################################################################


def setup_ros_parameters():
    '''
    Returns the gateway parameters from the ros param server.
    Most of these should be fairly self explanatory.
    '''
    param = {}

    # Check if there is a user provided custom configuration
    try:
        custom_configuration_file = rospy.get_param('~custom_rules_file')
        if custom_configuration_file:
            if os.path.isfile(custom_configuration_file):
                loaded_parameters = rosparam.load_file(custom_configuration_file, default_namespace=rospy.resolve_name(rospy.get_name()))  # this sets the private namespace
                for params, ns in loaded_parameters:
                    # need to merge whatever default rules are already on the param server with these settings
                    existing_parameters = rosparam.get_param(ns)
                    for p, v in params.iteritems():
                        if p in ['default_flips', 'default_advertisements', 'default_pulls'] and p in existing_parameters:
                            existing_parameters[p] += v
                        else:
                            existing_parameters[p] = v
                    rosparam.upload_params(ns, existing_parameters, verbose=True)
            else:
                rospy.logwarn("Gateway : user provided configuration file could not be found [%s]" % custom_configuration_file)
    except KeyError:
        # Not an error, just no need to load a custom configuration
        pass

    # Hub
    param['hub_uri'] = rospy.get_param('~hub_uri', '')
    # Convert these back to accepting lists once https://github.com/ros/ros_comm/pull/218
    # goes through, for now we use semi-colon separated lists.
    param['hub_whitelist'] = rospy.get_param('~hub_whitelist', [])
    param['hub_blacklist'] = rospy.get_param('~hub_blacklist', [])

    # Gateway
    param['name'] = rospy.get_param('~name', 'gateway')
    param['watch_loop_period'] = rospy.get_param('~watch_loop_period', 10)  # in seconds

    # Blacklist used for advertise all, flip all and pull all commands
    param['default_blacklist'] = rospy.get_param('~default_blacklist', [])  # list of Rule objects

    # Used to block/permit remote gateway's from flipping to this gateway.
    param['firewall'] = rospy.get_param('~firewall', True)

    # The gateway can automagically detect zeroconf, but sometimes you want to force it off
    param['disable_zeroconf'] = rospy.get_param('~disable_zeroconf', False)

    # The gateway uses uui'd to guarantee uniqueness, but this can be disabled
    # if you want clean names without uuid's (but you have to manually
    # guarantee uniqueness)
    param['disable_uuids'] = rospy.get_param('~disable_uuids', False)

    # Make everything publicly available (excepting the default blacklist)
    param['advertise_all'] = rospy.get_param('~advertise_all', [])  # boolean

    # Topics and services for pre-initialisation/configuration
    param['default_advertisements'] = rospy.get_param('~default_advertisements', [])  # list of Rule objects
    param['default_flips'] = rospy.get_param('~default_flips', [])  # list of RemoteRule objects
    param['default_pulls'] = rospy.get_param('~default_pulls', [])  # list of RemoteRule objects

    # Network interface name (to be used when there are multiple active interfaces))
    param['network_interface'] = rospy.get_param('~network_interface', '')  # string

    return param


def generate_rules(param):
    '''
      Converts a param of the suitable type (see default_blacklist.yaml)
      into a dictionary of Rule types.

      @return all rules as gateway_msgs.msg.Rule objects in our usual keyed dictionary format
      @rtype type keyed dictionary of Rule lists
    '''
    rules = utils.create_empty_connection_type_dictionary()
    for value in param:
        rule = Rule()
        rule.name = value['name']
        # maybe also check for '' here?
        pattern = re.compile("None", re.IGNORECASE)
        if pattern.match(value['node']):
            rule.node = ''  # ROS Message fields should not be None, maybe not a problem here though, see below
        else:
            rule.node = value['node']
        rule.type = value['type']
        rules[rule.type].append(rule)
    return rules


def generate_remote_rules(param):
    '''
       Converts a param of the suitable type (default_flips, default_pulls) into
       a list of RemoteRule objects and a list of target gateways for flip_all/pull_all.

       @param yaml object
       @type complicated

       @return list of remote rules
       @return RemoteRule[]
    '''
    remote_rules = []
    all_targets = []
    pattern = re.compile("None", re.IGNORECASE)
    for remote_rule in param:
        if 'rule' in remote_rule:
            # maybe also check for '' here?
            node = None if pattern.match(remote_rule['rule']['node']) else remote_rule['rule']['node']
            remote_rules.append(RemoteRule(remote_rule['gateway'],
                                           Rule(remote_rule['rule']['type'],
                                                remote_rule['rule']['name'],
                                                node
                                                )
                                           )
                                )
        else:
            all_targets.append(remote_rule['gateway'])
    return remote_rules, all_targets
