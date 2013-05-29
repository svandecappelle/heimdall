#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser

"""The error flag used to log"""
ERROR=0
"""The warning flag used to log"""
WARN=1
"""The info flag used to log"""
INFO=2
"""The debug flag used to log"""
DEBUG=3

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.read('heimdall.conf')

"""The rsa repository to check"""
DEPOT=config.get("folders", "deposit_dir")
"""The heimdall database file"""
DB_FILE=config.get("folders", "sqlite_database")

"""The ssh service port"""
SSH_PORT=config.getint("sshd", "port")
"""Configuration to send file when access is open or close to admin"""
notifyAdminByMail=config.get("notifications", "notify_admin_by_mail") == "yes"
"""Configuration to send file when access is open or close to affected user"""
notifyUserByEmail=config.get("notifications", "notify_user_by_mail") == "yes"
"""Not used for the moment. In future version. """
heimdallEmail=config.get("notifications", "heimdall_email")
"""Admin notification email"""
administratorEmail=config.get("notifications", "administrator_email")
"""Admin notification email"""
ccAdmins=config.get("notifications", "cc_administrators")
"""Not used for the moment. In future version."""
heimdallHost=config.get("notifications", "heimdall_host")
