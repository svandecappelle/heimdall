#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The MIT License

Copyright (c) 2013-2014 Vekia Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


Authors: 
- Vandecappelle Steeve<svandecappelle@vekia.fr>
- Sobczak Arnaud<asobczack@vekia.fr>
"""

import os,sys
from lib.ReplicationFactory import ReplicationFactory
from lib.utils.Logger import Logger
from lib.utils import Constants
from lib.datas.DataBaseConnector import DataBaseConnector
from lib.datas.RequestBinder import RequestBinder
from lib.datas.RequestBinder import Request

logger = Logger("Controller",Constants.INFO)


def addUser():
	"""
	Add a user to the heimdall database.
	"""
	
	values = list()
	values.append(raw_input("Username? "))
	values.append(raw_input("Real name? "))
	values.append(raw_input("Email? "))
	
	insertUser = Request("USER")
    	insertUser.setMode("INSERT")
    	insertUser.addSelect("USER_NAME")
    	insertUser.addSelect("NAME")
    	insertUser.addSelect("EMAIL")
	
    	insertUser.addValues(values[0])
    	insertUser.addValues(values[1])
    	insertUser.addValues(values[2])

    	connector = DataBaseConnector(Constants.DB_FILE)
    	userQuery = RequestBinder(connector)

    	userQuery.execQuery(insertUser);

	logger.log("User created", Constants.INFO)
	
	selectUser = Request("USER")
	selectUser.addWhere("USER_NAME = '"+values[0]+"'")
    	userQuery.execQuery(selectUser)
	connector.database.close()

def addServer():
	"""
	Add a server to the heimdall database.
	"""
	logger.log("addServer",Constants.DEBUG)
	server = raw_input("Server Host? ")
	serverDesc = raw_input("Any description on this server ?")
	addPermission = raw_input("Do you want to add some permission to this server?")
	
	insertServer = Request("SERVERS")
	insertServer.setMode("INSERT")
	insertServer.addSelect("SERVER_NAME")
	insertServer.addSelect("DESCRIPTION")
	
	insertServer.addValues(server)
	insertServer.addValues(serverDesc)

	connector = DataBaseConnector(Constants.DB_FILE)
	serverQuery = RequestBinder(connector)
	serverQuery.execQuery(insertServer)

	selectServer = Request("SERVERS")
        selectServer.addWhere("SERVER_NAME = '"+server+"'")
        serverQuery.execQuery(selectServer)
        connector.database.close()
	
def addPermission():
	"""
	Grant a permission to an existing server and an existing user on database.
	If the user has already uploaded his rsa key, then the replicator replicate 
	his key on the server to instant grant access.
	"""
	
	server = raw_input("Server to add permission?")
	user = raw_input("User to add permission?")
	hostuser = raw_input("Wich user you want to open access to?")
	
	insertPermission = Request("SERVER_PERMISSIONS")
	insertPermission.setMode("INSERT")
	insertPermission.addSelect("SERVER_NAME")
	insertPermission.addSelect("USER_NAME")
	insertPermission.addSelect("LOGIN")
	
	insertPermission.addValues(server)
	insertPermission.addValues(user)
	insertPermission.addValues(hostuser)
	
	connector =  DataBaseConnector(Constants.DB_FILE)
	createPermissionQuery = RequestBinder(connector)
	createPermissionQuery.execQuery(insertPermission)
	logger.log("permission added", Constants.INFO)
	replicate(user, server, hostuser, True)

def revokePermission():
	"""
	Revoke a permission to an existing server and an existing user on database.
	If the user has already uploaded his rsa key, then the replicator revoke 
	his key on the server.
	"""
	server = raw_input("Server to revoke permission?")
        user = raw_input("User to revoke permission?")
        hostuser = raw_input("Wich user you want to revoke access to?")

        deletePermission = Request("SERVER_PERMISSIONS")
        deletePermission.setMode("DELETE")
        deletePermission.addWhere("SERVER_NAME  = '" + server + "' AND USER_NAME = '"+ user+"' AND LOGIN = '"+hostuser+"'")

        connector =  DataBaseConnector(Constants.DB_FILE)
        revokePermissionQuery = RequestBinder(connector)
	revokePermissionQuery.execQuery(deletePermission)	
	logger.log("Permission revoked", Constants.INFO)
	replicate(user, server, hostuser,False)

def removeServer():
	"""
	Remove a server from the database.
	Note: it will no revoke the access granted.
	"""
	logger.log("removeServer", Constants.DEBUG)

def showServerPermission():
	"""
	Show all access oppened to a server by heimdall.
	"""
	server = raw_input("Server to show permission?")
	
	connector = DataBaseConnector(Constants.DB_FILE)
        serverPermissionQuery = RequestBinder(connector)

	selectServer = Request("SERVER_PERMISSIONS")
	selectServer.addWhere("SERVER_NAME = '"+server+"'")
	serverPermissionQuery.execQuery(selectServer)
        connector.database.close()


def showUsers():
	"""
	Show all user added into the heimdall database.
	"""
	logger.log("Users: ", Constants.INFO)
	
	connector = DataBaseConnector(Constants.DB_FILE)
        showUsersQuery = RequestBinder(connector)
	
	selectUser = Request("USER")
        showUsersQuery.execQuery(selectUser)
        connector.database.close()

## redifine
def showRsa():
	"""
	Show the users RSA keys.
	"""
	logger.log("Show RSA ids", Constants.INFO)
        connector = DataBaseConnector(Constants.DB_FILE)
        showRsaQuery = RequestBinder(connector)

        selectRsaIdPub = Request("RSA_ID")
	showRsaQuery.execQuery(selectRsaIdPub)
        connector.database.close()
def delRsa():
	"""
	Delete a rsa key from the heimdall database.
	The user associated need to re-upload a new one to grant new access.
	Note: it will no revoke the access granted.
	"""
	logger.log("Delete RSA ids", Constants.INFO)
	user = raw_input("User to delete rsa id?")

        connector = DataBaseConnector(Constants.DB_FILE)
        deleteRsaQuery = RequestBinder(connector)
        deleteRsaIdPub = Request("RSA_ID")
	deleteRsaIdPub.setMode("DELETE")
        deleteRsaIdPub.addWhere("USER_NAME  = '" + user + "'")
	deleteRsaQuery.execQuery(deleteRsaIdPub)
        connector.database.close()
	
def showServers():
	"""
	Show all servers added into heimdall database.
	"""
	logger.log("Servers: ", Constants.INFO)
        connector = DataBaseConnector(Constants.DB_FILE)
        showServersQuery = RequestBinder(connector)

        selectUser = Request("SERVERS")
	showServersQuery.execQuery(selectUser)
        connector.database.close()


def replicate(user,server, hostuser,add):
	"""
	Replicate an access to a server for a user.
	"""
	logger.log("replicate modification data",Constants.INFO)
	
	connector = DataBaseConnector(Constants.DB_FILE)
        selectRsaQuery = RequestBinder(connector)
        selectRsaIdPub = Request("RSA_ID")
	selectRsaIdPub.setIsPrint(False)
        selectRsaIdPub.addWhere("USER_NAME  = '" + user + "'")
	result = selectRsaQuery.execQuery(selectRsaIdPub)

	row = result.fetchone()
	try:
		key_rsa = str(row[1])

		connector.database.close()
		replicator = ReplicationFactory()

		if add:
			logger.log("Adding access for server: "+server+" to " + user + " on "+ hostuser, Constants.INFO)
			replicator.replicate_one_server(server, hostuser,key_rsa, user)
		else:
			logger.log("Revoking access for server: "+server+" to " + user + " on "+ hostuser, Constants.INFO)
			replicator.delete_replication(server, hostuser,key_rsa,  user)

	except Exception, e:
		logger.log("Failed to revoke access: "+server+" to " + user + " on "+ hostuser + " check the users RSA_ID on database:\n "+ str(e), Constants.ERROR)
	

