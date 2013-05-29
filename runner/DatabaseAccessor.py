#!/usr/bin/python2.7
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

# Name:         DatabaseAccessor.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

import ConfigurationFiles
import Controller

from runner import *
from lib.utils.Logger import Logger
from lib.utils import Constants
from lib.utils.Messager import Messager
from lib.datas import DataBaseConnector
from lib.datas import RequestBinder


logger = Logger("DatabaseAccessor",Constants.DEBUG)
class Accessor:
	def whatYouWantRead(self):
		"""
		Read the standard input to make configure rights in interactive command.
		You can:
		 * add user / server
		 * show users/ servers
		 * grant access / revoke access
		 * remove server 
		 * show access permissions
		 * exit the program 
		"""
	
		Messager.printm("What do you want to do ?","blue")
		Messager.printm("1. Add user","green")
		Messager.printm("2. Add server","green")
		Messager.printm("3. Add user permission","green")
		Messager.printm("4. Revoke user permission","magenta")
		Messager.printm("5. Remove server from list","magenta")
		Messager.printm("6. Show a server permissions","cyan")
		Messager.printm("7. Show users","cyan")
		Messager.printm("8. Show servers","cyan")
		Messager.printm("9. Exit","green")
	
		print
		
		choice = input("choice: ")
		
		if choice == 1: 
			Controller.addUser()
		elif choice == 2:
			Controller.addServer()
		elif choice == 3:
			Controller.addPermission()
		elif choice == 4:
			Controller.revokePermission()
		elif choice == 5:
			Controller.removeServer()
		elif choice == 6:
			Controller.showServerPermission()
		elif choice == 7:
			Controller.showUsers()
		elif choice == 8:
			Controller.showServers()
		elif choice == 9:
			exit()
		elif choice == 999:
			Controller.showRsa()
		elif choice == 998:
			Controller.delRsa()
		else:
			logger.log("Invalid choice.",Constants.ERROR)
			whatYouWantRead()
			
		print
		print
		
	
		self.whatYouWantRead()
	
	def start(self):
		config = ConfigurationFiles.ConfigurationFiles(Constants.DB_FILE)
		self.whatYouWantRead()


