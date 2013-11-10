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

# Name:         bastion/lib/utils/Constants.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""
# import ConfigParser

"""The error flag used to log"""
ERROR = int(0)
"""The warning flag used to log"""
WARN = int(1)
"""The info flag used to log"""
INFO = int(2)
"""The debug flag used to log"""
DEBUG = int(3)

# config = ConfigParser.RawConfigParser(allow_no_value=True)
# config.read('heimdall.conf')

"""The rsa repository to check"""
# DEPOT=config.get("folders", "deposit_dir")
"""The heimdall database file"""
# DB_FILE=config.get("folders", "sqlite_database")
"""The ssh service port"""
SSH_PORT = 22
"""Configuration to send file when access is open or close to admin"""
notifyAdminByMail = True
"""Configuration to send file when access is open or close to affected user"""
notifyUserByEmail = True
"""Not used for the moment. In future version. """
heimdallEmail = "heimdall@heimdall.fr"
"""Admin notification email"""
administratorEmail = "heimdall@heimdall.fr"
"""Admin notification email"""
ccAdmins = []
"""Send mail through server mail."""
mailGateway = "gateway"
