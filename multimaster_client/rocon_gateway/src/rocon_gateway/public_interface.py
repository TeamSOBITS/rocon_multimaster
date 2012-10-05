#!/usr/bin/env python
#       
# License: BSD
#   https://raw.github.com/robotics-in-concert/rocon_multimaster/master/multimaster_client/rocon_gateway/LICENSE 
#

##############################################################################
# Imports
##############################################################################

import copy
import yaml
import re

import rospy

# local imports
import utils
from gateway_comms.msg import PublicRule as PublicRuleMsg

##############################################################################
# Public
##############################################################################

class PublicRule(object):
    '''
      Holds a rule defining the properties for a single connection flip.
    '''
    def __init__(self, type, regex, node = None):
        self.type = type
        self.regex = regex
        self.node = node
    
    # Need these for hashable containers (like sets), ugh!
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.type) ^ hash(self.regex) ^ hash(self.node)
    
    def __repr__(self):
        return '{ type: %s name/regex: %s node name: %s }'%(self.type,self.regex,self.node)

    def toMessage(self):
        msg = PublicRuleMsg()
        msg.type = self.type
        msg.name = self.regex
        node = self.node
        if node == None:
            node = ''
        msg.node = node
        return msg

    @classmethod
    def fromMessage(cls, message):
        node = message.node
        if node == '':
            node = None
        return cls(message.type, message.name, node)

    @classmethod
    def fromDict(cls, data_dict):
        node = data_dict['node']
        if node == '':
            node = None
        return cls(data_dict['type'],data_dict['name'], node)

    @classmethod
    def fromMessageListToRuleList(cls, msg_list):
        rules = []
        for msg in msg_list:
            rules.append(cls.fromMessage(msg))
        return rules

    @classmethod
    def fromRuleListToMessageList(cls, rules):
        msg_list = []
        for rule in rules:
            msg_list.append(rule.toMessage())
        return msg_list
        
##############################################################################
# Public Interface
##############################################################################

class PublicInterface(object):
    '''
      The public interface is the set of connections (pubs/subs/services/actions)
      that are exposed and made available for freely sharing with a multimaster system.
      
      It consists of two parts:
      
       * list of currently available connections to be shared
       * list of connections and filters that will be watched 
         and shared if they become available 
      
      Q) Filters should be in the form of whitelists/blacklists or just whitelists?
    '''
    def __init__(self):
        self._public = set()
        self._watchlist = set()
        self._default_blacklisted_rules = set()
        self._blacklisted_rules = self._default_blacklisted_rules

    ##########################################################################
    # Public Interfaces
    ##########################################################################

    def addRule(self,rule):
        '''
        Attempt to add a connection to the public interface. 
        
        @param rule : a rule parsed from the advertise call
        @type PublicRule
        @return True if the rule was added, False if the rule exists already
        @rtype bool
        '''
        if rule in self._watchlist:
            return False
        else:
            self._watchlist.add(rule)
        return True

    def removeRule(self,rule):
        '''
        Attempt to remove a connection from the public interface.
        
        @param rule : a rule parsed from the advertise call
        @type PublicRule
        @return True if the rule was removed, False if rule did not exist
        @rtype bool
        '''
        if rule not in self._watchlist:
            return False
        else:
            self._watchlist.remove(rule)
        return True

    def allowAll(self, blacklist = None):
        '''
        Allow all rules apart from the ones in the blacklist
        '''
        self._watchlist = set()
        for connection in utils.getConnectionTypes():
            self._watchlist.add(connection,'.*')
        self._blacklisted_rules = copy.deepcopy(self._default_blacklisted_rules)
        self._blacklisted_rules |= blacklist

    def disallowAll(self):
        '''
        Disallow all rules
        '''
        self.rules = set()
        self._blacklisted_rules = self._default_blacklisted_rules

    def add(self,connection):
        if connection in self._public:
            return False
        else:
            self._public.add(connection)
        return True

    def remove(self,connection):
        if connection not in self._public:
            return False
        else:
            self._public.remove(connection)
        return True

    ##########################################################################
    # File operations
    ##########################################################################

    def _parseRulesFromFile(self,rules,file):
        try:
            stream = open(file, 'r')
            list = yaml.load(stream)
        except:
            rospy.logerr('Gateway : Unable to load yaml from file [%s]'%file)
            return False

        add_rules = set()
        try:
            for l in list:
                rule = PublicRule.fromDict(l)
                add_rules.add(rule)
        except Exception as e:
            rospy.logerr('Gateway : Error parsing item in yaml file [%s]'%str(e))
            return False
        rules |= add_rules
        return True;

    def parseDefaultRulesFromFile(self,file):
        if self._parseRulesFromFile(self._watchlist,file):
            rospy.loginfo('Gateway : Default public interface parsed from yaml file [%s]'%file)
            return True
        else:
            rospy.logerr('Gateway : Error parsing default public interface from yaml file [%s]'%file)
            return False

    def parseBlacklistFromFile(self,file):
        if self._parseRulesFromFile(self._default_blacklisted_rules,file):
            rospy.loginfo('Gateway : Default blacklist parsed from yaml file [%s]'%file)
            return True
        else:
            rospy.logerr('Gateway : Error parsing default blacklist from yaml file [%s]'%file)
            return False

    ##########################################################################
    # Filter
    ##########################################################################

    def _matchAgainstRuleList(self,rules,type,name,node):
        for rule in rules:
            if rule.type == type and re.match(rule.regex, name):
                if not rule.node:
                    return rule
                elif node == rule.node:
                    return rule
                else:
                    return None
            else:
                return None

    def matchesRule(self,type,name,node):
        rule = self._matchAgainstRuleList(self._watchlist)
        if rule and self._matchAgainstRuleList(self._blacklisted_rules):
            rule = None
        return rule

    def isPublic(self,connection):
        return connection in self._public



