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

# Name:         ReplicationFactory.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

from paramiko import SSHClient
from paramiko import SSHException
from paramiko import AutoAddPolicy
from paramiko import AuthenticationException

from email.mime.text import MIMEText
import socket, smtplib

from heimdall.bastion.lib.utils import Constants
from heimdall.bastion.lib.utils.Logger import Logger


logger = Logger("ReplicationFactory", Constants.DEBUG)

class ReplicationFactory: 
	def replicate_one_server(self, server, userhost, key_rsa, userName, usermail):
		'''Replicate access on one server for one user'''
		try:
			client = SSHClient()
			client.load_system_host_keys()
			client.set_missing_host_key_policy(AutoAddPolicy())
			client.connect('%s' % server, port=Constants.SSH_PORT, username=userhost)    
		
			# ## Insert permission into server authorized_keys ssh file
			stdin, stdout, stderr = client.exec_command("echo '%s' >> .ssh/authorized_keys" % key_rsa)
			
		except AuthenticationException as e:
			logger.log("Error Authentication: " + str(e), Constants.ERROR)
		except SSHException as e:
			logger.log("Error SSH: " + str(e), Constants.ERROR)
		except socket.error as e:  # be carefull of NO ROUTE TO HOST exception
			logger.log("Error Socket: " + str(e), Constants.ERROR)
		except Exception as e:
			logger.log("Not catched error on replication: " + str(e), Constants.ERROR)
			
		client.close()
		self.notify(server, userName, userhost, False, usermail)

	def revoke_one_server(self, server, userhost, key_rsa, userName, usermail):
		"""
		Delete a heimdall replication.
		"""
		try:
			client = SSHClient()
			client.load_system_host_keys()
			client.set_missing_host_key_policy(AutoAddPolicy())
			client.connect('%s' % server, port=Constants.SSH_PORT, username=userhost)    
		
			# ## Insert permission into server authorized_keys ssh file
			sshconfig_file = "~/.ssh/authorized_keys"
			rsa_search = str(key_rsa).replace('\r\n', '').replace('\r', '').replace('\n', '') 
			
			stdin, stdout, stderr = client.exec_command("grep -v '%s' %s > %s.tmp" % (rsa_search, sshconfig_file, sshconfig_file))
			stdin, stdout, stderr = client.exec_command("cat %s > %s.bak" % (sshconfig_file, sshconfig_file))
			stdin, stdout, stderr = client.exec_command("rm %s" % (sshconfig_file))
			stdin, stdout, stderr = client.exec_command("mv %s.tmp %s" % (sshconfig_file, sshconfig_file))
			stdin, stdout, stderr = client.exec_command("rm %s.bak" % (sshconfig_file))
			logger.log("Access revoked", Constants.INFO)
		except AuthenticationException as e:
			logger.log(e, Constants.ERROR)
		except SSHException as e:
			logger.log(e, Constants.ERROR)
		except socket.error as e:  # be carefull of NO ROUTE TO HOST exception
			logger.log(e, Constants.ERROR)
		except Exception as e:
			logger.log("Not catched error on replication: " + str(e) , Constants.ERROR)
		client.close()	
		self.notify(server, userName, userhost, True, usermail)

	def notify(self, server, trig, user, isRevoke, usermail):
		"""
		Notify the user and admin if config constant is enable to
		"""
		if Constants.notifyAdminByMail:
			logger.log("Notify admin by email", Constants.INFO)
			if isRevoke:
				self.alertToAdmin('An administrator has just revoke access on %s to %s user connected with %s' % (server, trig, user), server);
			else:
				self.alertToAdmin('An administrator has just open access on %s to %s user connected with %s' % (server, trig, user), server);
			
			
		if Constants.notifyUserByEmail:
			logger.log("Notify user by email", Constants.INFO)
			if isRevoke:
				self.alertToUser('An administrator has just revoke access for you account on %s to %s user connected with %s' % (server, trig, user), trig, server, usermail);
			else:
				self.alertToUser('An administrator has just open access for you account on %s to %s user connected with %s' % (server, trig, user), trig, server, usermail);
			
		logger.log("Replication finished", Constants.INFO)
	
	
	def alertToAdmin(self, message, server):
		'''Alert by email the admins'''
		# Create an html message
		msg = MIMEText(message,'html')

		s = smtplib.SMTP(Constants.heimdallHost)
		
		sender = Constants.heimdallEmail
		recipients = [Constants.administratorEmail] + Constants.ccAdmins
		msg['Subject'] = 'Heimdall notification access to %s' % server
		msg['From'] = sender
		msg['To'] = ", ".join(recipients)
		s.sendmail(sender, recipients, msg.as_string())
		s.quit()
		
	def alertToUser(self, message, trig, server, usermail):
		'''Alert by email the user who granted / revoked'''
		userEmail = usermail;
		
		s = smtplib.SMTP(Constants.heimdallHost)
		# Create an html message
		msg = MIMEText(message,'html')
		
		sender = Constants.heimdallEmail
		msg['Subject'] = 'Heimdall notification access to %s' % server
		msg['From'] = sender
		msg['To'] = userEmail
		s.sendmail(sender, userEmail, msg.as_string())
		s.quit()
	