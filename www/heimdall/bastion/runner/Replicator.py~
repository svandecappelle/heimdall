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

# Name:         Replicator.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

from lib import *
from lib.utils.Logger import Logger
from lib.utils import Constants
from ConfigurationFiles import ConfigurationFiles
from lib.ReplicationFactory import ReplicationFactory

logger = Logger("Replicator", Constants.DEBUG)

class Replicator:

	def start(self):
		logger.log("Starting replicator daemon.",Constants.INFO)
		config = ConfigurationFiles(Constants.DB_FILE)
	
		replicator = ReplicationFactory()
		logger.log("Started replicator...",Constants.INFO)
		replicator.watch()
