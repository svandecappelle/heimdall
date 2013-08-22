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

# Name:         ConfigurationFiles.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

import os,sys

from lib.utils.Logger import Logger
from lib.utils import Constants
from lib.datas.RequestBinder import RequestBinder
from lib.datas.DataBaseConnector import DataBaseConnector
from lib.datas.RequestBinder import RequestBinder
from lib.datas.RequestBinder import Request
from lib.datas.RequestBinder import Table


logger = Logger("ConfigurationFiles",3)

class ConfigurationFiles:
	"""
	Check the needed files to start the heimdall service.
	Note: Change the needed files path through the config file: Constants.py
	"""

	def __init__(self, *configuration_files):
		self.exist = False
		self.files = configuration_files
		for file in self.files:
			if not os.path.exists(file):
				logger.log('Database does not exist, creating... ', Constants.WARN)
				## Function that creates database
				self.createConfigFile(file)
			else:
				self.exist = True
				#watch()
				logger.log('Database already exist, configure...',Constants.INFO)
	   
	def createConfigFile(self, file):
		logger.log("Config file: [ "+ file + "] not existing.", Constants.INFO)
		self.createDB(file)
		
	
	def createDB(self, file):
		'''Create database schema'''
		logger.log("Creating db "+ file,Constants.INFO)
		connector = DataBaseConnector(file)
		creationDbQuery = RequestBinder(connector)
	
		tableUser = Table("USER","USER_NAME","NAME","EMAIL")
		tableUser.add_pk_constraint("USER_NAME_PK","USER_NAME")
		creationDbQuery.create(tableUser)
	
		tableServer = Table("SERVERS","SERVER_NAME","DESCRIPTION")
		tableServer.add_pk_constraint("SERVER_NAME_PK","SERVER_NAME")
		creationDbQuery.create(tableServer)
	
		tableServer = Table("SERVER_PERMISSIONS","SERVER_NAME","USER_NAME","LOGIN")
		tableServer.add_fk_constraint("SERVER_NAME_FK", "SERVER_NAME","SERVERS","SERVER_NAME")
		tableServer.add_fk_constraint("USER_NAME_FK", "USER_NAME","USERS","USER_NAME")
		creationDbQuery.create(tableServer)
	
		tableRsaIdPub = Table("RSA_ID","USER_NAME","RSA UNIQUE NOT NULL")
		tableRsaIdPub.add_pk_constraint("RSA_ID_PK", "USER_NAME")
		tableRsaIdPub.add_fk_constraint("USER_NAME_FK", "USER_NAME" , "USER" , "USER_NAME")
		creationDbQuery.create(tableRsaIdPub)
	
		creationDbQuery.executeQuery("PRAGMA foreign_keys = ON")
	
		connector.database.close()	

