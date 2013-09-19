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

# Name:         Logger.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

import datetime
from heimdall.bastion.lib.utils.termcolor import colored
from heimdall.bastion.lib.utils import Constants 

class Logger:
	"""
	Logger of heimdall. It log by log level on the standard output.
	Shows: 
	* DateTime
	* LogLevel (ERROR,WARN,INFO,DEBUG)
	* LogFile Source
	* Message
	"""
	
	def __init__(self, source, *level):
		if level:
			self.level = level
		else:
			self.level = Constants.INFO
			
		self.source = source
		self.ERROR = Constants.ERROR
		self.WARN = Constants.WARN
		self.INFO = Constants.INFO
		self.DEBUG = Constants.DEBUG

	def get_log(self, level, message):
		return "[" + self.source + ".py] " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "  - " + str(level) + " - \
		" + str(message)

	def log_warn(self, message):
		if self.level >= self.WARN:
			print(self.get_log("WARN", message))

	def log(self, message, level_log):
		if self.level >= level_log:
			print(colored(self.get_log(self.getLevel(level_log), message), self.getColor(level_log)))

	def debug(self, message):
		if self.level >= Constants.DEBUG:
			print(colored(self.get_log(self.getLevel(Constants.DEBUG), message), self.getColor(Constants.DEBUG)))

	def info(self, message):
		print(self.level)
		if self.level >= Constants.INFO:
			print(colored(self.get_log(self.getLevel(Constants.INFO), message), self.getColor(Constants.INFO)))

	def warn(self, message):
		if self.level >= Constants.WARN:
			print(colored(self.get_log(self.getLevel(Constants.WARN), message), self.getColor(Constants.WARN)))
		
	def error(self, message):
		if self.level >= Constants.ERROR:
			print(colored(self.get_log(self.getLevel(Constants.ERROR), message), self.getColor(Constants.ERROR)))

	def getLevel(self, level):
		if level == 0:
			return "ERROR"
		elif level == 1:
			return "WARN"		
		elif level == 2:
			return "INFO"
		elif level == 3:
			return "DEBUG"

	def getColor(self, level):
		if level == 0:
			return "red"
		elif level == 1:
			return "red"		
		elif level == 2:
			return "white"
		elif level == 3:
			return "yellow"

