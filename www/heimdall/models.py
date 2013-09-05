from django.db import models
from django.contrib.auth.models import User

class Server(models.Model):
	hostname = models.CharField(max_length=50)
	description = models.CharField(max_length=250)
	def __unicode__(self):
		return u"%s" % (self.hostname)

class Permission(models.Model):
	user = models.ForeignKey(User)
	server = models.ForeignKey(Server)
	hostuser = models.CharField(max_length=50)
	def __unicode__(self):
		return u"%s->%s->%s" % (self.user.username,self.server.hostname,self.hostuser)
		
class SshKeys(models.Model):
	user = models.ForeignKey(User)
	key = models.CharField(max_length=4000)
	host = models.CharField(max_length=250)

class Roles(models.Model):
	ROLES_CHOICES = (
	    ('ADMIN', 'ADMIN'),
	    ('MANAGER', 'MANAGER'),
	    ('USER', 'USER'),
	)
	name = models.CharField(max_length=250)
	type=models.CharField(max_length=50, choices=ROLES_CHOICES)
	description = models.CharField(max_length=1500)
	
class UserRoles(models.Model):
	user = models.ForeignKey(User)
	role = models.ForeignKey(Roles)
	
class RolePerimeter(models.Model):
	server = models.ForeignKey(Server)
	roles = models.ForeignKey(Roles)
	def __unicode__(self):
		return u"%s->%s" % (self.server.hostname,self.roles.name)

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
	cdate = models.DateField()
	close_date = models.DateField(null=True, blank=True)
	
	def __unicode__(self):
		return u"%s->%s->%s" % (self.user.username,self.server.hostname,self.hostuser)
