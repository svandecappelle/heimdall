#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
heimdallEmail = "toto@dlsn.fr"
"""Admin notification email"""
administratorEmail = "toto@dlsn.fr"
"""Admin notification email"""
ccAdmins = []
"""Not used for the moment. In future version."""
heimdallHost = "host"
