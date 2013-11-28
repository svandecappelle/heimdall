#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

This file is part of Heimdall.

Heimdall is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Heimdall is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Heimdall.  If not, see <http://www.gnu.org/licenses/>. 

Authors: 
- Vandecappelle Steeve<svandecappelle@vekia.fr>
- Sobczak Arnaud<asobczack@vekia.fr>

# Name:         templatetags/tags.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""


from django import template
from django.template import resolve_variable, NodeList
from django.contrib.auth.models import Group

from heimdall.models import HeimdallUserRole, HeimdallPool, Server, PoolPerimeter

register = template.Library()

@register.tag()
def ifusergroup(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifusergroup Admins %} ... {% endifusergroup %}, or
           {% ifusergroup Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokensp = token.split_contents()
        groups = []
        groups += tokensp[1:]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifusergroup' requires at least 1 argument.")
    
    nodelist_true = parser.parse(('else', 'endifusergroup'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifusergroup',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return GroupCheckNode(groups, nodelist_true, nodelist_false)

class GroupCheckNode(template.Node):
    def __init__(self, groups, nodelist_true, nodelist_false):
        self.groups = groups
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = resolve_variable('user', context)
        
        if not user.is_authenticated():
            return self.nodelist_false.render(context)
        
        allowed = False
        for checkgroup in self.groups:
            try:
                group = Group.objects.get(name=checkgroup)
            except Group.DoesNotExist:
                break
                
        if group in user.groups.all():
            allowed = True
        
        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
            
            




@register.tag()
def ifisa(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifusergroup User Admins %} ... {% endifusergroup %}, or
           {% ifusergroup User Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokensp = token.contents.split()
        user = tokensp[1]
        groups = []
        groups += tokensp[2:]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifisa' requires at least 2 arguments.")
    
    nodelist_true = parser.parse(('else', 'endifisa'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifisa',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return GroupCheck(user, groups, nodelist_true, nodelist_false)




@register.tag()
def ifhasroletype(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifhasroletype Admins %} ... {% ifhasroletype %}, or
           {% ifhasroletype Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokensp = token.contents.split()
        roletype = tokensp[1]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifhasroletype' requires exactly 1 arguments.")
    
    nodelist_true = parser.parse(('else', 'endifhasroletype'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifhasroletype',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return RoleTypeCheck(roletype, nodelist_true, nodelist_false)



@register.tag()
def ifpoolandtype(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifhasroletype Admins %} ... {% ifhasroletype %}, or
           {% ifhasroletype Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokensp = token.contents.split()
        pool = tokensp[1]
        roletype = tokensp[2]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifpoolandtype' requires at least 2 arguments.")
    
    nodelist_true = parser.parse(('else', 'endifpoolandtype'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifpoolandtype',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return PoolNameAndTypeCheck(pool, roletype, nodelist_true, nodelist_false)

@register.tag()
def ifpoolserverandtype(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifhasroletype Admins %} ... {% ifhasroletype %}, or
           {% ifhasroletype Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokensp = token.contents.split()
        server = tokensp[1]
        roletype = tokensp[2]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifpoolserverandtype' requires at least 2 arguments.")
    
    nodelist_true = parser.parse(('else', 'endifpoolserverandtype'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifpoolserverandtype',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return PoolServerNameAndTypeCheck(server, roletype, nodelist_true, nodelist_false)


class PoolServerNameAndTypeCheck(template.Node):
    def __init__(self, server, roleType, nodelist_true, nodelist_false):
        self.roleType = roleType
        self.server = server
        
        if "{{" in self.server :
            self.server = self.server.replace("{","")
            self.server = self.server.replace("}","")
            self.server = template.Variable(self.server)
            self.needToResolve = True
        else:
            self.server = self.server
            self.needToResolve = False

        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = resolve_variable('user', context)
        if self.needToResolve:
            serverNameConcrete = self.server.resolve(context)
        else:
            serverNameConcrete = self.server
        
        serverObject = Server.objects.get(hostname=serverNameConcrete)
        pools = PoolPerimeter.objects.filter(server=serverObject).values_list('pool')
        
        allowed = HeimdallUserRole.objects.filter(user=user,pool__in=pools, type=self.roleType).exists()
        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)



class PoolNameAndTypeCheck(template.Node):
    def __init__(self, pool, roleType, nodelist_true, nodelist_false):
        self.roleType = roleType
        self.pool = pool
          
        if "{{" in self.pool :
            self.pool = self.pool.replace("{","")
            self.pool = self.pool.replace("}","")
            self.poolname = template.Variable(self.pool)
            self.needToResolve = True
        else:
            self.poolname = self.pool
            self.needToResolve = False

        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = resolve_variable('user', context)
        if self.needToResolve:
            poolnameConcrete = self.poolname.resolve(context)
        else:
            poolnameConcrete = self.poolname
            
        poolObject = HeimdallPool.objects.get(name=poolnameConcrete)
        allowed = HeimdallUserRole.objects.filter(user=user,pool=poolObject, type=self.roleType).exists()
        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)

class RoleTypeCheck(template.Node):
    def __init__(self, roleType, nodelist_true, nodelist_false):
        self.roleType = roleType
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = resolve_variable('user', context)
        allowed = HeimdallUserRole.objects.filter(user=user, type=self.roleType).exists()
        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
            



@register.tag()
def ifhasrole(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifhasroletype Admins %} ... {% ifhasroletype %}, or
           {% ifhasroletype Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokensp = token.contents.split()
        user = tokensp[1]
        roletype = tokensp[2]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifhasrole' requires at least 2 arguments.")
    
    nodelist_true = parser.parse(('else', 'endifhasrole'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifhasrole',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return RoleCheck(user, roletype, nodelist_true, nodelist_false)


class RoleCheck(template.Node):
    def __init__(self, oneusername, role, nodelist_true, nodelist_false):
        self.role = role
        self.oneusername = oneusername
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = resolve_variable(self.oneusername, context)
        role = resolve_variable(self.role, context)
        
        pool = HeimdallPool.objects.get(name=role);
        if HeimdallUserRole.objects.filter(user=user, pool = pool):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


class GroupCheck(template.Node):
    def __init__(self, oneusername, groups, nodelist_true, nodelist_false):
        self.groups = groups
        self.oneusername = oneusername
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = resolve_variable(self.oneusername, context)
        
        allowed = False
        for checkgroup in self.groups:
            try:
                group = Group.objects.get(name=checkgroup)
            except Group.DoesNotExist:
                try:
                    checkgroup = resolve_variable(checkgroup, context)
                    group = Group.objects.get(name=checkgroup)
                except Group.DoesNotExist:
                    break
                break
                
            
        if group in user.groups.all():
            allowed = True
        
        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
            

