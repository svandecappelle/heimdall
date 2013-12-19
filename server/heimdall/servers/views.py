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

# Name:         servers/views.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

from django.template import RequestContext
from django.shortcuts import render_to_response

from heimdall import utils
from heimdall.models import Server, Permission


def servers(request):
    list_servers = Server.objects.all()
    args = utils.give_arguments(request.user, 'Serveurs')
    args.update({'list_servers': list_servers})

    return render_to_response('servers.html', args, context_instance=RequestContext(request))


def permissions(request):
    all_permissions = Permission.objects.all()
    userConnected = request.user

    args = utils.give_arguments(request.user, 'Permissions')
    if userConnected.is_authenticated:
        if userConnected.groups.filter(name="heimdall-admin"):
            args.update({'permissions': convertToIterable(all_permissions)})
        elif userConnected.groups.filter(name="heimdall"):
            if Permission.objects.filter(user=userConnected).exists():
                permissions_visible = Permission.objects.filter(user=userConnected)

                args.update({'permissions': convertToIterable(permissions_visible)})
    return render_to_response('user/permissions.html', args, context_instance=RequestContext(request))


def convertToIterable(permissions_visible):
    try:
        iter(permissions_visible)
        permissions_visible_to_return = permissions_visible
    except TypeError:
        permissions_visible_to_return = [1]
        permissions_visible_to_return[0] = permissions_visible

    return permissions_visible_to_return
