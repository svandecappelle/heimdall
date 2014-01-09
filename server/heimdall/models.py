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

# Name:         models.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

from django.db import models
from django.contrib.auth.models import User


class Server(models.Model):
	hostname = models.CharField(max_length=50)
	description = models.CharField(max_length=250)
	port = models.IntegerField()

	def __unicode__(self):
		return u"%s" % (self.hostname)


class Permission(models.Model):
	user = models.ForeignKey(User)
	server = models.ForeignKey(Server)
	hostuser = models.CharField(max_length=50)

	def __unicode__(self):
		return u"%s->%s [%s]" % (self.user.username, self.server.hostname, self.hostuser)


class SshKeys(models.Model):
	user = models.ForeignKey(User)
	key = models.CharField(max_length=4000)


class HeimdallPool(models.Model):
	name = models.CharField(max_length=250)

	def __unicode__(self):
		return u"%s" % (self.name)


class HostedUsers(models.Model):
	username = models.CharField(max_length=250)
	server = server = models.ForeignKey(Server)

	def __unicode__(self):
		return u"%s" % (self.username)


class HeimdallUserRole(models.Model):
	ROLES_CHOICES = (('ADMIN', 'ADMIN'), ('MANAGER', 'MANAGER'), ('USER', 'USER'),)
	type = models.CharField(max_length=50, choices=ROLES_CHOICES)
	user = models.ForeignKey(User)
	pool = models.ForeignKey(HeimdallPool)

	def __unicode__(self):
		return u"%s | %s [[%s]]" % (self.pool.name, self.user.username, self.type)


class PoolPerimeter(models.Model):
	server = models.ForeignKey(Server)
	pool = models.ForeignKey(HeimdallPool)

	def __unicode__(self):
		return u"%s | %s" % (self.server.hostname, self.pool.name)


class Demands(models.Model):
	PRIORITY_CHOICES = (('HIGH', 'HIGH'), ('NORMAL', 'NORMAL'), ('LOW', 'LOW'),)
	user = models.ForeignKey(User)
	server = models.ForeignKey(Server)
	hostuser = models.CharField(max_length=50)
	priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
	comments = models.CharField(max_length=4000, null=True, blank=True)
	accepted = models.NullBooleanField(null=True, blank=True)
	markAsIgnore = models.NullBooleanField(null=True, blank=True)
	cdate = models.DateTimeField()
	close_date = models.DateTimeField(null=True, blank=True)

	def __unicode__(self):
		return u"%s->%s->%s" % (self.user.username, self.server.hostname, self.hostuser)


class UserConfiguration(models.Model):
	user = models.ForeignKey(User)
	value = models.CharField(max_length=500)
	key = models.CharField(max_length=150)

	def __unicode__(self):
		return u"%s->%s" % (self.user.username, self.key)


class GeneralConfiguration(models.Model):
	value = models.CharField(max_length=500)
	key = models.CharField(max_length=150)

	def __unicode__(self):
		return u"%s" % (self.key)


class PendingThread(models.Model):
	process = models.CharField(max_length=500)
	pending_request = models.IntegerField()

	def __unicode__(self):
		return u"%s" % (self.process)
