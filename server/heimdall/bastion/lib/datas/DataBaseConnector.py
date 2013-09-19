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

# Name:         DataBaseConnector.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""
from heimdall.models import Server, Permission, Demands, SshKeys

class DataBaseConnector:
	"""
	Classe definissant une connection a une base SQLite.
	"""
  
	def __init__(self, file):
		self.file = file

	def connect(self):
		"""
		Connect a database file. SQLite
		"""
		self.database = sqlite3.connect(self.file)
		self.database.isolation_level = None
		return self.database.cursor()

	def disconnect(self):
		"""
		Disconnect a database file. SQLite
		"""
		self.database.close()
