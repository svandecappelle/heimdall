#-*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from heimdall.models import Server,Permission, Demands,SshKeys
from heimdall.objects import Statistics
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import User, Group
from datetime import date
from heimdall.form import UploadSshKeyForm
from django.core.urlresolvers import reverse
from heimdall import utils

from heimdall.bastion.runner import Controller
	
def user(request):
	args = utils.give_arguments(request, 'Users admin')
	if request.user.groups.filter(name="heimdall-admin"):
		args.update({'list_users': Group.objects.get(name="heimdall").user_set.all()})
		return render_to_response('admin/user.html', args, context_instance=RequestContext(request))
	else:
		args.update({'NOTIFICATION': 'You have not the rights to see this page'})	
		return render_to_response('index.html', args, context_instance=RequestContext(request))	

def permissions(request):
	Controller.showServers()
	demands = Demands.objects.all()
	servers = Server.objects.all()	
	users = User.objects.all()
	
	args = utils.give_arguments(request, 'Permissions admin')
	args.update({'demands' : demands, 'servers': servers, 'users': users})
	return render_to_response('admin/permissions.html', args, context_instance=RequestContext(request))

def grant_access(request):
	args = utils.give_arguments(request,'Permission admin')
	
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			if request.POST['username'] != '[[ALL]]':
				user = User.objects.get(username=request.POST['username'])
			else:
				print('TODO: look after demands')

			if request.POST['hostname'] != '[[ALL]]':
				host = Server.objects.get(hostname=request.POST['hostname'])
			else:
				print('TODO: look after demands')

			if request.POST['hostuser'] != '[[ALL]]':
				hostuser = request.POST['hostuser']
			else:
				print('TODO: look after demands')					
						
			# TODO activate this function
			#Controller.addPermission(user,host,hostuser)
			
			if request.POST['username'] != '[[ALL]]':
				message = 'Permission granted on: '+host.hostname + ' with ' + hostuser + ' (for the user '+ user.username+')' 
			else:
				message = 'All requested permissions granted'
			args.update({'NOTIFICATION': message})
	else:
		args.update({'NOTIFICATION': 'You have not the rights to do this action'})	

	demands = Demands.objects.all()
	servers = Server.objects.all()	
	users = User.objects.all()
	args.update({'demands' : demands, 'servers': servers, 'users': users})	

	return render_to_response('admin/permissions.html', args, context_instance=RequestContext(request))

def register_user(request):
	print("adduser")
	args = utils.give_arguments(request,'Permission admin')
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			if check_password(request.POST['password'],request.POST['password-confirm']):


				code_return_check = check_params(request.POST['password'],request.POST['username'],request.POST['email'],request.POST['firstname'],request.POST['lastname']) 
				print("return code ",str(code_return_check))
				if code_return_check == 1:
				
					group = None
					if request.POST['role'] == 'ADMIN':
						group = Group.objects.get(name='heimdall-admin')
					else:
						group = Group.objects.get(name='heimdall')
					
					new_user = User.objects.create_user(username=request.POST['username'],email=request.POST['email'],password=request.POST['password'],first_name=request.POST['firstname'],last_name=request.POST['lastname'])
					new_user.groups.add(group)
					new_user.save()
					args.update({'NOTIFICATION': 'User created'})
					
				elif code_return_check == 0:
					args.update({'NOTIFICATION': 'You need to fill all the blanks fields'})
				elif code_return_check == 2:
					args.update({'NOTIFICATION': 'The username already exists'})
				elif code_return_check == 3:
					args.update({'NOTIFICATION': 'The email you enterred is already associated with another account'})
				
			else:
				args.update({'NOTIFICATION': 'Password and password confirmation does not match'})
	else:
		args.update({'NOTIFICATION': 'You have not the rights to do this action'})
	
	return render_to_response('admin/user.html', args, context_instance=RequestContext(request))	
	#User()

def check_password(password, password_confirm):
	if password == password_confirm:
		return True
	else:
		return False

def check_params(password, username_target, email_target, firstname, lastname):
	output = 0
	if password != "" :
		if username_target != "":
			if email_target != "":
				if firstname != "":
					if lastname != "":
						output = 1
	
	if User.objects.filter(username=username_target):
		output = 2
	else:
		if User.objects.filter(email=email_target):
			output = 3
	
	return output
