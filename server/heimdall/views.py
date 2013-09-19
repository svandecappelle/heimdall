# -*- coding: utf-8 -*-
# Create your views here.
from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from heimdall import utils
from heimdall.form import UploadSshKeyForm
from heimdall.models import Server, Permission, Demands, SshKeys
from heimdall.objects import Statistics

def index(request):
	user_count = Group.objects.get(name="heimdall").user_set.all().count()
	server_count = Server.objects.all().count()
	keys_count = SshKeys.objects.all().count()
	demands_count = Demands.objects.filter(close_date__isnull=True).all().count()
	
	permissions_count = Permission.objects.all().count()
	stats = Statistics(user_count, server_count, permissions_count, demands_count, keys_count)
	
	demands = Demands.objects.filter(close_date__isnull=True).all()
	
	args = utils.give_arguments(request, 'Acceuil')
	args.update({'stats': stats, 'demands':demands})

	return render_to_response('index.html', args, context_instance=RequestContext(request))
	
def users(request):
	list_users = User.objects.all()
	
	args = utils.give_arguments(request, 'Utilisateurs')
	args.update({'list_users': list_users})
	
	return render_to_response('users.html', args , context_instance=RequestContext(request))
	
def servers(request):
	list_servers = Server.objects.all()
	args = utils.give_arguments(request, 'Serveurs')
	args.update({'list_servers': list_servers})

	return render_to_response('servers.html', args, context_instance=RequestContext(request))
	
def permissions(request):
	all_permissions = Permission.objects.all()
	userConnected = request.user

	args = utils.give_arguments(request, 'Permissions')
	if userConnected.is_authenticated:
		if userConnected.groups.filter(name="heimdall-admin"):
			args.update({'permissions': convertToIterable(all_permissions)})
		elif userConnected.groups.filter(name="heimdall"):
			permissions_visible = Permission.objects.get(user=userConnected)
			args.update({'permissions': convertToIterable(permissions_visible)})
	return render_to_response('permissions.html', args, context_instance=RequestContext(request))

def convertToIterable(permissions_visible):
	try:
		some_object_iterator = iter(permissions_visible)
		permissions_visible_to_return = permissions_visible
	except TypeError:
		permissions_visible_to_return = [1]
		permissions_visible_to_return[0] = permissions_visible

	return permissions_visible_to_return

def deposite(request):
	userConnected = request.user
	# Handle file upload
	docfile = []
	if request.method == 'POST':
		if request.POST['type'] == 'update':
			keysend = request.POST['key']
			sshkey = None
			if SshKeys.objects.filter(user=userConnected).count() > 0:
				sshkey = SshKeys.objects.get(user=userConnected)
				sshkey.key = keysend
				print("send key: " + keysend)
			else:
				sshkey = SshKeys(user=userConnected, key=keysend)
			
			sshkey.save()
			# Redirect to the document list after POST
			return HttpResponseRedirect(reverse('deposite'))
		else:
			form = UploadSshKeyForm(request.POST, request.FILES)
			if form.is_valid():
				docfile = request.FILES['docfile']
				for line in docfile:
					if SshKeys.objects.filter(user=userConnected).count() > 0:
						oldkey = SshKeys.objects.get(user=userConnected)
						oldkey.key = line
					else:
						sshkey = SshKeys(user=userConnected, key=line)
						sshkey.save()
				# Redirect to the document list after POST
				return HttpResponseRedirect(reverse('deposite'))
	else:
		if SshKeys.objects.filter(user=userConnected).count() > 0:
			key = SshKeys.objects.get(user=userConnected).key
		else:
			key = None
			
		form = UploadSshKeyForm()

	args = utils.give_arguments(request, 'Depot')
	args.update({'documents': docfile, 'form': form, 'key':key})
	return render_to_response('deposite.html', args, context_instance=RequestContext(request))
	
def connect(request):
	args = utils.give_arguments(request, 'Connect')
	return render_to_response('connect.html', args, context_instance=RequestContext(request))
	

def auth():
	if user is not None:
		# the password verified for the user
		if user.is_active:
			print("User is valid, active and authenticated")
		else:
			print("The password is valid, but the account has been disabled!")
	else:
		# the authentication system was unable to verify the username and password
		print("The username and password were incorrect.")
	


def mylogin(request):
	if request.method == 'POST':
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			if user.is_active:
				login(request, user)
				# success
				messages.success(request, 'Logged in')
				return HttpResponseRedirect(reverse('index'))
			else:
				messages.success(request, 'Your account was disabled by administrator. Please contact an administrator.')
				return HttpResponseRedirect(reverse('index'))
		else:
			# invalid login
			messages.success(request, 'Wrong username or password.')
			return HttpResponseRedirect(reverse('index'))
	else:
		messages.success(request, 'This page is not accessible.')
		return HttpResponseRedirect(reverse('index'))

def mylogout(request):
	logout(request)
	return HttpResponseRedirect('home')
	
def register(request):
	args = utils.give_arguments(request, 'Register')
	return render_to_response('register.html', args, context_instance=RequestContext(request))

def register_action(request):
	if request.method == 'POST':
		messages.success(request, 'User registered successfully.')
		return HttpResponseRedirect(reverse('index'))
		
	else:
		messages.success(request, 'This page is not accessible.')
		return HttpResponseRedirect(reverse('index'))
	
def require_access(request):
	if request.method == 'POST':
		userConnected = request.user
		if userConnected.is_authenticated:
			if userConnected.groups.filter(name="heimdall"):
				serverHost = Server.objects.get(hostname=request.POST['server'])
				userHost = request.POST['user']
				priority = request.POST['priority']
				comments = request.POST['comments']
				cdate = date.today()
				demand = Demands(user=userConnected, server=serverHost, hostuser=userHost, priority=priority, comments=comments, cdate=cdate)
				demand.save()
				
				messages.success(request, 'Notification sent to an heimdall administrator.')
				return HttpResponseRedirect(reverse('servers'))
			elif userConnected.groups.filter(name="heimdall-admin"):
				serverHost = Server.objects.get(hostname=request.POST['server'])
				userHost = request.POST['user']
				priority = request.POST['priority']
				comments = request.POST['comments']
				cdate = date.today()
				demand = Demands(user=userConnected, server=serverHost, hostuser=userHost, priority=priority, comments=comments, cdate=cdate)
				demand.save()
				
				messages.success(request, 'Notification sent to an heimdall administrator for: ' + request.user.username)
				return HttpResponseRedirect(reverse('servers'))
		else:
			messages.success(request, 'You need to be connected to see this page.')
			return HttpResponseRedirect(reverse('index'))
	else:
		messages.success(request, 'This page is not accessible.')
		return HttpResponseRedirect(reverse('index'))
