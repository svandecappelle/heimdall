#!/usr/bin/python2.7
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


