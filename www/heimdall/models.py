from django.db import models

# Create your models here.

class User(models.Model):
	username = models.CharField(max_length=50)
	firstname = models.CharField(max_length=200)
	lastname = models.CharField(max_length=200)
	rsaid = models.CharField(max_length=4096)

class Server(models.Model):
	hostname = models.CharField(max_length=50)
	description = models.CharField(max_length=250)

class Permission(models.Model):
	user = models.ForeignKey(User)
	server = models.ForeignKey(Server)
	hostuser = models.CharField(max_length=50)
