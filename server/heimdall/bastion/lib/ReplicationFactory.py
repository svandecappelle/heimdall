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

# Name:         bastion/lib/ReplicationFactory.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

from paramiko import SSHClient
from paramiko import AutoAddPolicy

from email.mime.text import MIMEText
import smtplib

import logging

from heimdall import utils

logger = logging.getLogger("ReplicationFactory")


class ReplicationFactory:
	def replicate_one_server(self, server, userhost, key_rsa, userName, usermail, port):
		'''Replicate access on one server for one user'''
		client = SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(AutoAddPolicy())
		client.connect('%s' % server, port=port, username=userhost)

		# ## Insert permission into server authorized_keys ssh file
		stdin, stdout, stderr = client.exec_command("echo '%s' >> .ssh/authorized_keys" % key_rsa)
		client.close()
		self.notify(server, userName, userhost, False, usermail)

	def revoke_one_server(self, server, userhost, key_rsa, userName, usermail, port):
		"""
		Delete a heimdall replication.
		"""
		client = SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(AutoAddPolicy())
		client.connect('%s' % server, port=port, username=userhost)

		# ## Insert permission into server authorized_keys ssh file
		sshconfig_file = "~/.ssh/authorized_keys"
		rsa_search = str(key_rsa).replace('\r\n', '').replace('\r', '').replace('\n', '')

		stdin, stdout, stderr = client.exec_command("grep -v '%s' %s > %s.tmp" % (rsa_search, sshconfig_file, sshconfig_file))
		stdin, stdout, stderr = client.exec_command("cat %s > %s.bak" % (sshconfig_file, sshconfig_file))
		stdin, stdout, stderr = client.exec_command("chmod 0600 %s.tmp" % (sshconfig_file))
		#stdin, stdout, stderr = client.exec_command("rm %s" % (sshconfig_file))
		stdin, stdout, stderr = client.exec_command("mv %s.tmp %s" % (sshconfig_file, sshconfig_file))
		stdin, stdout, stderr = client.exec_command("rm %s.bak" % (sshconfig_file))
		logger.info("Access revoked")
		client.close()
		self.notify(server, userName, userhost, True, usermail)

	def notify(self, server, trig, user, isRevoke, usermail):
		"""
		Notify the user and admin if config constant is enable to
		"""

		logger.info("Notify users by email")
		if isRevoke:
			self.alertToAdmin('An administrator has just revoke access on %s to %s user connected with %s' % (server, trig, user), server, usermail)
		else:
			self.alertToAdmin('An administrator has just open access on %s to %s user connected with %s' % (server, trig, user), server, usermail)
		logger.info("Replication finished")

	def alertToAdmin(self, message, server, userEmail):
		'''Alert by email the admins and the user if configured'''
		# Create an html message
		msg = MIMEText(message, 'html')
		s = smtplib.SMTP(utils.getConfigurationAdmin('mail_server_hostname'))

		sender = utils.getConfigurationAdmin('mail_system_user_account')
		recipients = [utils.getConfigurationAdmin('mail_system_user_account')]
		msg['Subject'] = 'Heimdall permissions changed on %s' % server
		msg['From'] = sender

		if utils.getConfigurationAdmin('user_notification') == 'true':
			msg['To'] = userEmail
			recipients = [utils.getConfigurationAdmin('mail_system_user_account'), userEmail]
		else:
			msg['To'] = ", ".join(recipients)

		if utils.getConfigurationAdmin('admin_notification') == 'true' and not utils.getConfigurationAdmin('user_notification') == 'false':
			msg['Cc'] = ", ".join(recipients)

		s.sendmail(sender, recipients, msg.as_string())
		s.quit()
