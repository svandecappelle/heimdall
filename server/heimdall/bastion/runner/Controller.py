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

# Name:         Controller.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

from heimdall.bastion.lib.ReplicationFactory import ReplicationFactory
from heimdall.bastion.lib.utils.Logger import Logger
from heimdall.bastion.lib.utils import Constants

from heimdall.models import Permission

logger = Logger("WebController")
replicator = ReplicationFactory()
	
def addPermission(user_target, server_target, hostuser_target, sshkey):
	"""
	Grant a permission to an existing server and an existing user on database.
	If the user has already uploaded his rsa key, then the replicator replicate 
	his key on the server to instant grant access.
	"""
	logger.log("Add permission: " + user_target.username + " for server: ["+server_target.hostname+"]" + " with user: {"+hostuser_target+"}", Constants.INFO)
	permission = Permission(user=user_target, server=server_target, hostuser=hostuser_target)
	replicator.replicate_one_server(server_target.hostname, hostuser_target, sshkey.key, user_target.username, user_target.email, server_target.port)
	permission.save()
	logger.log("permission added need replicate", Constants.INFO)

def revokePermission(user_target, server_target, hostuser_target, sshkey):
	"""
	Revoke a permission to an existing server and an existing user on database.
	If the user has already uploaded his rsa key, then the replicator revoke 
	his key on the server.
	"""
	logger.log("Revoke permission ", Constants.INFO)
	permission = Permission.objects.filter(user=user_target, server=server_target, hostuser=hostuser_target)
	replicator.revoke_one_server(server_target.hostname, hostuser_target, sshkey.key, user_target.username, user_target.email, server_target.port)
	permission.delete()
	logger.log("permission added need replicate", Constants.INFO)