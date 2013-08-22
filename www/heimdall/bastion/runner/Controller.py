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

import os,sys
from heimdall.bastion.lib.ReplicationFactory import ReplicationFactory
from heimdall.bastion.lib.utils.Logger import Logger
from heimdall.bastion.lib.utils import Constants
from heimdall.bastion.lib.datas.DataBaseConnector import DataBaseConnector
from heimdall.bastion.lib.datas.RequestBinder import RequestBinder
from heimdall.bastion.lib.datas.RequestBinder import Request

from heimdall.models import Server,Permission, Demands,SshKeys

logger = Logger("WebController")


def addUser():
	"""
	Add a user to the heimdall database.
	"""
	logger.log("User created", Constants.INFO)

def addServer():
	"""
	Add a server to the heimdall database.
	"""
	logger.log("addServer",Constants.DEBUG)
	
def addPermission(user_target,server_target,hostuser_target):
	"""
	Grant a permission to an existing server and an existing user on database.
	If the user has already uploaded his rsa key, then the replicator replicate 
	his key on the server to instant grant access.
	"""
	permission = Permission(user=user_target,server=server_target,hostuser=hostuser_target)
	permission.save()
	# TODO replicate
	logger.log("permission added need replicate", Constants.INFO)

def revokePermission():
	"""
	Revoke a permission to an existing server and an existing user on database.
	If the user has already uploaded his rsa key, then the replicator revoke 
	his key on the server.
	"""
	logger.log("Permission revoked", Constants.INFO)

def removeServer():
	"""
	Remove a server from the database.
	Note: it will no revoke the access granted.
	"""
	logger.log("removeServer", Constants.DEBUG)

def showUsers():
	"""
	Show all user added into the heimdall database.
	"""
	logger.log("Users: ", Constants.INFO)

def delRsa():
	"""
	Delete a rsa key from the heimdall database.
	The user associated need to re-upload a new one to grant new access.
	Note: it will no revoke the access granted.
	"""
	logger.log("Delete RSA ids", Constants.INFO)
	
def showServers():
	"""
	Show all servers added into heimdall database.
	"""
	print(Constants.INFO)
	logger.info("Servers: ")
	list_servers = Server.objects.all()
	print(list_servers)


def replicate(user,server, hostuser,add):
	"""
	Replicate an access to a server for a user.
	"""
	logger.log("replicate modification data",Constants.INFO)
	
#	connector = DataBaseConnector(Constants.DB_FILE)
#	selectRsaQuery = RequestBinder(connector)
#	selectRsaIdPub = Request("RSA_ID")
#	selectRsaIdPub.setIsPrint(False)
#	selectRsaIdPub.addWhere("USER_NAME  = '" + user + "'")
#	result = selectRsaQuery.execQuery(selectRsaIdPub)
#
#	row = result.fetchone()
#	try:
#		key_rsa = str(row[1])
#
#		connector.database.close()
#		replicator = ReplicationFactory()#
#
#		if add:#
#			logger.log("Adding access for server: "+server+" to " + user + " on "+ hostuser, Constants.INFO)
#			replicator.replicate_one_server(server, hostuser,key_rsa, user)
#		else:
#			logger.log("Revoking access for server: "+server+" to " + user + " on "+ hostuser, Constants.INFO)
#			replicator.delete_replication(server, hostuser,key_rsa,  user)
#
#	except Exception:
#		logger.log("Failed to revoke access: "+server+" to " + user + " on "+ hostuser + " check the users RSA_ID on database:\n " , Constants.ERROR)
	

