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
	
class HeimdallUserRole(models.Model):	
	ROLES_CHOICES = (
	    ('ADMIN', 'ADMIN'),
	    ('MANAGER', 'MANAGER'),
	    ('USER', 'USER'),
	)
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
	PRIORITY_CHOICES = (
	    ('HIGH', 'HIGH'),
	    ('NORMAL', 'NORMAL'),
	    ('LOW', 'LOW'),
	)
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
