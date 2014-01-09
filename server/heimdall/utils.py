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

# Name:         utils.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

from django.shortcuts import render_to_response
from django.template import RequestContext

from heimdall.models import Demands, UserConfiguration, GeneralConfiguration, Permission

from paramiko import SSHClient
from paramiko import AutoAddPolicy

import logging
import socket

logger = logging.getLogger("ReplicationFactory")


class VoidDemand(tuple):
	count = 0


def getConfiguration(user, conf_id):
	output = None
	if GeneralConfiguration.objects.filter(key=conf_id).exists():
		if GeneralConfiguration.objects.get(key=conf_id).value == 'default':
			output = None
		else:
			output = GeneralConfiguration.objects.get(key=conf_id).value
	else:
		output = None
	if user:
		if user.is_authenticated():
			if UserConfiguration.objects.filter(user=user, key=conf_id).exists():
				if UserConfiguration.objects.get(user=user, key=conf_id).value == 'default':
					output = None
				else:
					output = UserConfiguration.objects.get(user=user, key=conf_id).value

	return output


def getAvailableUsersInHost(host):
	usersForbidden = getConfigurationAdmin('forbidden_users')
	if usersForbidden is not None:
		matches = usersForbidden.replace(',', '|')
	else:
		matches = ""

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(2)
	try:
		sock.connect((host.hostname, host.port))
	except socket.error:
		print("Server" + host.hostname + " offline")
		sock.close()
		return []
	#print("SSH connection")
	try:
		userConfigured = []

		client = SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(AutoAddPolicy())
		if Permission.objects.get(server=host).exists():
			print("try connect with: " + str(Permission.objects.get(server=host)[:1]) + " on: " + host.hostname)
			client.connect('%s' % host.hostname, port=host.port, username=Permission.objects.get(server=host)[:1])

			# Check user allowed to replicator
			stdin, stdout, stderr = client.exec_command("cut -d':' -f1 /etc/passwd | grep --invert-match -E '%s'" % matches)
			output = stdout.readlines()
			client.close()

			for user in output:
				# print("test with: " + user.strip())
				# TODO find a solution for test without worst performance
				#if test_connection(host, user.strip()):
				userConfigured.append(user.strip())

			logger.info("All users configured for " + host.hostname + " are: " + str(userConfigured))
		else:
			print("None permissions yet configured. Need at least one.")
		return userConfigured

	except:
		return []


def test_connection(host, user):
	try:
		client = SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(AutoAddPolicy())
		client.connect('%s' % host.hostname, port=host.port, username=user)
		stdin, stdout, stderr = client.exec_command("uptime")
		output = stdout.read()
		client.close()
		if output is None or output == "":
			return False
		return True
	except:
		return False


def getConfigurationAdmin(conf_id):
	output = None
	if GeneralConfiguration.objects.filter(key=conf_id).exists():
		if GeneralConfiguration.objects.get(key=conf_id).value == 'default':
			output = None
		else:
			output = GeneralConfiguration.objects.get(key=conf_id).value
	else:
		output = None
	return output


def theme(user):
	output = None
	if GeneralConfiguration.objects.filter(key='theme').exists():
		if GeneralConfiguration.objects.get(key='theme').value == 'default':
			output = None
		else:
			output = GeneralConfiguration.objects.get(key='theme').value
	else:
		output = None
	if user:
		if user.is_authenticated():
			if UserConfiguration.objects.filter(user=user, key='theme').exists():
				if UserConfiguration.objects.get(user=user, key='theme').value == 'default':
					output = None
				else:
					output = UserConfiguration.objects.get(user=user, key='theme').value

	return output


def give_arguments(user, page_title):
	return {'PAGE_TITLE': page_title, 'theme': theme(user), 'APP_TITLE': "Heimdall", 'inbox_demands_count': get_demands_filtered(user).count}


# utils
def get_demands_filtered(user_filter):
	demands = VoidDemand()
	if user_filter.groups.filter(name="heimdall-admin").exists():
		demands = Demands.objects.filter(markAsIgnore=False)
	elif user_filter.groups.filter(name="heimdall").exists():
		demands = Demands.objects.filter(user=user_filter, markAsIgnore=False)
	return demands


def get_demands_filtered_and_read(user_filter):
	demands = VoidDemand()
	if user_filter.groups.filter(name="heimdall-admin").exists():
		demands = Demands.objects.filter(markAsIgnore=True)
	elif user_filter.groups.filter(name="heimdall").exists():
		demands = Demands.objects.filter(user=user_filter, markAsIgnore=True)
	return demands


def get_demands_filtered_pending(user_filter):
	demands = VoidDemand()
	if user_filter.groups.filter(name="heimdall-admin").exists():
		demands = Demands.objects.filter(close_date__isnull=True, markAsIgnore=False)
	elif user_filter.groups.filter(name="heimdall").exists():
		demands = Demands.objects.filter(user=user_filter, close_date__isnull=True, markAsIgnore=False)
	return demands


def get_all_demands_filtered_pending(user_filter):
	demands = VoidDemand()
	if user_filter.groups.filter(name="heimdall-admin").exists():
		demands = Demands.objects.filter(close_date__isnull=True)
	elif user_filter.groups.filter(name="heimdall").exists():
		demands = Demands.objects.filter(user=user_filter, close_date__isnull=True)
	return demands


def handler404(request):
	#args = give_arguments(request.user, 'Not found')
	return render_to_response('errors/404.html', {'PAGE_TITLE': "404", 'APP_TITLE': "Heimdall"}, context_instance=RequestContext(request))


def handler500(request):
	#args = give_arguments(request.user, 'Internal error')
	return render_to_response('errors/500.html', {'PAGE_TITLE': "500", 'APP_TITLE': "Heimdall"}, context_instance=RequestContext(request))
