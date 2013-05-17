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

