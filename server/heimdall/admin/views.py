# -*- coding: utf-8 -*-
# Create your views here.
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from heimdall import utils
from heimdall.bastion.runner import Controller
from heimdall.models import Server, Demands, SshKeys, Roles, RolePerimeter, UserRoles, Permission

def user(request):
	args = utils.give_arguments(request.user, 'Users admin')
	if request.user.groups.filter(name="heimdall-admin"):
		args.update({'list_users': Group.objects.get(name="heimdall").user_set.all()})
		return render_to_response('admin/user.html', args, context_instance=RequestContext(request))
	else:
		messages.success(request, 'You have not the rights to see this page')
		return HttpResponseRedirect(reverse('admin'))
	
def revoke_access(request):
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			user = User.objects.get(username=request.POST['username'])
			host = Server.objects.get(hostname=request.POST['hostname'])
			hostuser = request.POST['hostuser']
						
			rsa_key = SshKeys.objects.get(user=user)
			Controller.revokePermission(user, host, request.POST['hostuser'], rsa_key)
			
			message = 'Permission revoked on: ' + host.hostname + ' with ' + hostuser + ' (for the user ' + user.username + ')' 
			messages.success(request, message)
	else:
		messages.success(request, 'You have not the rights to do this action')

	return HttpResponseRedirect(reverse('admin-permissions'))

def create_server(request):
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			
			if request.POST['hostname']:
				server = Server(hostname=request.POST['hostname'], description= request.POST['description'])
				server.save()
				messages.success(request, 'Server created')
				return HttpResponseRedirect(reverse('servers'))
			messages.success(request, 'Form datas in errors. Check your parameters.')
			return HttpResponseRedirect(reverse('create-server'))
		else:
			return render_to_response('admin/create_server.html', context_instance=RequestContext(request))

	else:
		messages.success(request, 'You have not the rights to do this action')
	return HttpResponseRedirect(reverse('servers'))

def permissions(request):
	demands = Demands.objects.all()
	servers = Server.objects.all()	
	users = User.objects.all()
	permissions = Permission.objects.all()
	
	args = utils.give_arguments(request.user, 'Permissions admin')
	args.update({'demands' : demands, 'servers': servers, 'users': users, 'permissions' : permissions})
	return render_to_response('admin/permissions.html', args, context_instance=RequestContext(request))

def add_to_group(request):
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			user = User.objects.get(username=request.POST['username'])
			role = Roles.objects.get(name=request.POST['rolename'])
			
			new_userrole = UserRoles(user=user, role=role)
			new_userrole.save()
			
			messages.success(request, 'Role associated')
			return HttpResponseRedirect(reverse('admin-group-management'))
		else:
			messages.success(request, 'You have not the rights to do this action')
	else:
		messages.success(request, 'You have not the rights to do this action')
		
	return HttpResponseRedirect(reverse('admin-group-management'))

def manage_user_role(request):
	return render_to_response('admin/manage_user_role.html', context_instance=RequestContext(request))


def grant_access(request):
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			user = None
			host = None
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
						
			rsa_key = SshKeys.objects.get(user=user)
			Controller.addPermission(user, host, request.POST['hostuser'], rsa_key)
			
			if request.POST['username'] != '[[ALL]]':
				message = 'Permission granted on: ' + host.hostname + ' with ' + hostuser + ' (for the user ' + user.username + ')' 
				messages.success(request, message)
			else:
				messages.success(request, 'All requested permissions granted')
	else:
		messages.success(request, 'You have not the rights to do this action')

	return HttpResponseRedirect(reverse('admin-permissions'))

def manage_user_group(request):
	args = utils.give_arguments(request.user, 'User group')
	return render_to_response('admin/user_groups.html', args, context_instance=RequestContext(request))

def manage_groups(request):
	servers = Server.objects.all()	
	users = User.objects.all()
	
	userRoles = UserRoles.objects.all()
	roles = Roles.objects.all()
	groups = Group.objects.exclude(name="heimdall-admin").exclude(name="heimdall")
	
	args = utils.give_arguments(request.user, 'Group management')
	args.update({'groups' : groups, 'servers': servers, 'users': users, 'roles': roles, 'userRoles' : userRoles})	
	
	return render_to_response('admin/groups.html', args, context_instance=RequestContext(request))

def add_group(request):
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			if Roles.objects.filter(name=request.POST['groupname']).count() == 0:
				new_role = Roles(name=request.POST['groupname'], type=request.POST['grouptype'])
				new_role.save()
				messages.success(request, "Your data has been saved!")
			else:
				messages.success(request, "Group already exists")
			
			return HttpResponseRedirect(reverse('admin-group-management'))
			
	return render_to_response("index.html", context_instance=RequestContext(request))

def change_perimeter_role(request):
	if request.user.groups.filter(name="heimdall-admin"):
		servers = Server.objects.all()
		if request.method == 'POST':
			role = Roles.objects.get(name=request.POST['groupname'])
			server = Server.objects.get(hostname=request.POST['hostname'])
			role_perimeter = RolePerimeter.objects.filter(roles=Roles.objects.get(name=request.POST['groupname']))
			
			if request.POST['action'] == 'add':
				
				is_allow_to_add = RolePerimeter.objects.filter(roles=role, server=server).count() == 0
				print is_allow_to_add
				if is_allow_to_add:
					new_perimeter = RolePerimeter(roles=role, server=server)
					new_perimeter.save()
					role_perimeter = RolePerimeter.objects.filter(roles=Roles.objects.get(name=request.POST['groupname']))
					messages.success(request, "Group perimeter modified")
					return HttpResponseRedirect(reverse('admin-group-management'))
				else:                                                                                                    
					args = utils.give_arguments(request.user, 'Group management')
					messages.success(request, "Server already present in the perimeter")
					return HttpResponseRedirect(reverse('admin-group-management'))
					
			elif request.POST['action'] == 'remove':
				is_allow_to_remove = RolePerimeter.objects.filter(roles=role, server=server).count() == 1
				if is_allow_to_remove:
					
					perimeter_to_delete = RolePerimeter.objects.get(roles=role, server=server)
					perimeter_to_delete.delete()
					args = utils.give_arguments(request.user, 'Group management')
					messages.success(request, "Group perimeter modified")
					return HttpResponseRedirect(reverse('admin-group-management'))
				else:                                                                                                    
					args = utils.give_arguments(request.user, 'Group management')
					messages.success(request, "Server not present in the perimeter")
					return HttpResponseRedirect(reverse('admin-group-management'))
		else:
			role_perimeter = RolePerimeter.objects.filter(roles=Roles.objects.get(name=request.GET['groupname']))
			
			server_perimeter = []
			
			for role in role_perimeter:
				server_perimeter.append(role.server)
			
			args = utils.give_arguments(request.user, 'Group management')
			args.update({'perimeter': role_perimeter, 'servers' : servers, 'groupname': request.GET['groupname'], 'server_perimeter':server_perimeter })	
			return render_to_response("admin/role_perimeter.html", args, context_instance=RequestContext(request))

def register_user(request):
	print("adduser")
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			if check_password(request.POST['password'], request.POST['password-confirm']):
				code_return_check = check_params(request.POST['password'], request.POST['username'], request.POST['email'], request.POST['firstname'], request.POST['lastname']) 
				print("return code ", str(code_return_check))
				if code_return_check == 1:
					group = None
					if request.POST['role'] == 'ADMIN':
						group = Group.objects.get(name='heimdall-admin')
					else:
						group = Group.objects.get(name='heimdall')
					
					new_user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password'], first_name=request.POST['firstname'], last_name=request.POST['lastname'])
					new_user.groups.add(group)
					new_user.save()
					messages.success(request, "Server not present in the perimeter")
				elif code_return_check == 0:
					messages.success(request, "You need to fill all the blanks fields")
				elif code_return_check == 2:
					messages.success(request, "The username already exists")
				elif code_return_check == 3:
					messages.success(request, "The email you enterred is already associated with another account")
				
			else:
				messages.success(request, "Password and password confirmation does not match")
	else:
		messages.success(request, "Server not present in the perimeter")
		return HttpResponseRedirect(reverse('index'))
	
	return HttpResponseRedirect(reverse('admin-user'))

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
