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

# Name:         admin/views.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

from datetime import datetime

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from heimdall import utils
from heimdall.bastion.runner import Controller
from heimdall.models import Server, Demands, SshKeys, HeimdallPool, PoolPerimeter, HeimdallUserRole, Permission
from heimdall.models import GeneralConfiguration, UserConfiguration, HostedUsers, PendingThread
from heimdall.admin.threaded import RefreshingServersHosts


#Installation
def install(request):
	'''
	Installation function. This function create (if not exists) the heimdall's groups and default user.
	Accessible by /admin/install
	'''
	if not Group.objects.filter(name='heimdall').exists():
		user_group = Group.objects.create(name='heimdall')
		user_group.save()
	if not Group.objects.filter(name='heimdall-admin').exists():
		group = Group.objects.create(name='heimdall-admin')
		group.save()
	else:
		group = Group.objects.get(name='heimdall-admin')

	if not User.objects.filter(username='heimdall').exists():
		new_user = User.objects.create_user(username="heimdall", password="heimdall")
		new_user.groups.add(group)
		new_user.save()

	messages.success(request, 'Installation successfull. You can connect with heimdall')
	return render_to_response('admin/install.html', context_instance=RequestContext(request))


def app_config(request):
	'''
	Application configurations view. Can save user configuration such as language and theme.
	Accessible by /admin/app-config
	'''
	utils.getAvailableUsersInHost(Server.objects.get(hostname="georges"))
	args = utils.give_arguments(request.user, 'Users admin')

	if PendingThread.objects.filter(process='userhost-list-refresh').exists():
		thread = PendingThread.objects.get(process='userhost-list-refresh')
		messages.success(request, 'Server user host currently refreshing ' + str(thread.pending_request))

	admin_configs = ['theme', 'mail_server_hostname', 'mail_system_user_account', 'user_notification', 'admin_notification', 'forbidden_users']

	for field in admin_configs:
		args.update({field: utils.getConfiguration(request.user, field)})

	args.update({'default_theme': utils.getConfigurationAdmin('theme')})
	if request.user.is_authenticated():
		return render_to_response('admin/app_config.html', args, context_instance=RequestContext(request))
	else:
		messages.success(request, 'You have not the rights to do this action')
	return HttpResponseRedirect(reverse('index'))


def app_config_save(request):
	'''
	Save configurations on server.
	A POST form to save the server or user configurations.
	View Type: Form POST
	'''
	if request.method != 'POST':
		messages.success(request, 'This page is not accessible.')
		return HttpResponseRedirect(reverse('index'))

	globalConfiguredFields = ['theme', 'mail_server_hostname', 'admin_notification', 'user_notification', 'mail_system_user_account', 'forbidden_users']
	userConfiguredFields = ['theme']
	if 'type' in request.POST:
		if request.POST['type'] == 'global':
			for field in globalConfiguredFields:
				if field in request.POST:
					if request.user.groups.filter(name="heimdall-admin"):
						updateGeneralConfig(field, request.POST[field])
						messages.success(request, 'Saved global heimdall configurations.')
					else:
						messages.success(request, 'You have not the rights to do this action.')
				else:
					messages.success(request, 'Configuration cannot be saved. Not a parametrized config.')
	else:
		for field in userConfiguredFields:
			if field in request.POST:
				updateUserConfig(request.user, field, request.POST[field])
				messages.success(request, 'Saved user heimdall configurations.')
			else:
				messages.success(request, 'Configuration cannot be saved. Not a parametrized config.')
	return HttpResponseRedirect(reverse('app-config'))


def updateGeneralConfig(key_str, value_str):
	'''
	Update a server configuration key / value
	'''
	if GeneralConfiguration.objects.filter(key=key_str).exists():
		config = GeneralConfiguration.objects.get(key=key_str)
		config.value = value_str
	else:
		config = GeneralConfiguration(key=key_str)
		config.value = value_str
	config.save()


def updateUserConfig(user, key_str, value_str):
	'''
	Update a user configuration key / value
	'''
	if UserConfiguration.objects.filter(user=user, key=key_str).exists():
		config = UserConfiguration.objects.get(user=user, key=key_str)
		config.value = value_str
	else:
		config = UserConfiguration(user=user, key=key_str)
		config.value = value_str
	config.save()


def user(request):
	'''
	Get the user information.
	If 'me' parameter is in GET RequestContext, then return only my informations. Returns all users else. (if request.user is in admin group)
	View Type: Form GET
	'''
	args = utils.give_arguments(request.user, 'Users admin')
	only_me = True
	if 'me' in request.GET:
		if request.GET['me'] == 'n':
			only_me = False

	if request.user.groups.filter(name="heimdall-admin") and not only_me:
		users = list(Group.objects.get(name="heimdall").user_set.all())
		admin_users = Group.objects.get(name="heimdall-admin").user_set.all()

		for user in admin_users:
			if user not in users:
				users.append(user)

		args.update({'list_users': users, 'myaccount': only_me})
		return render_to_response('admin/user.html', args, context_instance=RequestContext(request))
	else:
		users = [request.user]
		args.update({'list_users': users, 'myaccount': only_me})
		return render_to_response('admin/user.html', args, context_instance=RequestContext(request))


def revoke_access(request):
	'''
	Revoke an access to a specified server.
	View Type: Form POST
	'''
	if request.method == 'POST':
		user = User.objects.get(username=request.POST['username'])
		host = Server.objects.get(hostname=request.POST['hostname'])
		hostuser = request.POST['hostuser']

		message = None

		if SshKeys.objects.filter(user=user).count == 0:
			message = 'No RSA saved on database. Contact user to set his RSA key.'
		elif SshKeys.objects.filter(user=user).count() > 1:
			message = 'More than one RSA saved on database. Contact administrator to set his RSA key.'
		else:
			rsa_key = SshKeys.objects.get(user=user)
			err = Controller.revokePermission(user, host, request.POST['hostuser'], rsa_key)
			if err is None:
				message = 'Permission revoked on: ' + host.hostname + ' with ' + hostuser + ' (for the user ' + user.username + ')'
				if Demands.objects.filter(user=user, server=host, hostuser=hostuser).exists():
					Demands.objects.get(user=user, server=host, hostuser=hostuser).delete()
			else:
				message = err.message

		messages.success(request, message)
	else:
		messages.success(request, 'You have not the rights to do this action')

	return HttpResponseRedirect(reverse('admin-permissions'))


def create_server(request):
	'''
	Create a server in models data. If POST Type: save a server, else get the server infos.
	View Type: Form POST / GET
	'''
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			if request.POST['hostname']:

				if Server.objects.filter(hostname=request.POST['hostname']).exists():
					server = Server.objects.get(hostname=request.POST['hostname'])
					server.description = request.POST['description']
					server.port = request.POST['port']
					messages.success(request, 'Server updated')

				else:
					server = Server(hostname=request.POST['hostname'], description=request.POST['description'], port=request.POST['port'])
					messages.success(request, 'Server created')

				server.save()

				return HttpResponseRedirect(reverse('servers'))

			messages.success(request, 'Form datas in errors. Check your parameters.')
			return HttpResponseRedirect(reverse('create-server'))
		else:
			if 'hostname' in request.GET:
				host = Server.objects.get(hostname=request.GET['hostname'])
				args = utils.give_arguments(request.user, 'Create server')

				args.update({'hostname': host.hostname, 'description': host.description, 'port': host.port})
				return render_to_response('admin/create_server.html', args, context_instance=RequestContext(request))
			return render_to_response('admin/create_server.html', context_instance=RequestContext(request))
	else:
		messages.success(request, 'You have not the rights to do this action')
	return HttpResponseRedirect(reverse('servers'))


def permissions(request):
	'''
	View getting all permissions visible for the user. Manager -> all user pool's permissions. Admin -> all permissions.
	View Type: Form GET
	'''
	if request.user.groups.filter(name="heimdall-admin"):
		args = getarguments_for_admin(request.user)
	else:
		args = getarguments_for_manager(request, request.user)

	return render_to_response('admin/permissions.html', args, context_instance=RequestContext(request))


def refresh_servers_hostuser(request):

	thread = RefreshingServersHosts()
	thread.run()

	messages.success(request, 'Currently refreshing...')
	return HttpResponseRedirect(reverse('app-config'))


def getarguments_for_admin(user):
	'''
	Get permissions to display in view for an admin user.
	'''
	servers = Server.objects.all()
	users = User.objects.all()
	demands = utils.get_all_demands_filtered_pending(user)
	permissions = Permission.objects.all()
	args = utils.give_arguments(user, 'Permissions admin')

	hostedUsers = HostedUsers.objects.all()
	#for server in servers:
	#	print(server.hostname)
	#	appendedUsers = utils.getAvailableUsersInHost(server)
	#
	#		for userToAdd in appendedUsers:
	#			if userToAdd not in hostedUsers:
	#				hostedUsers.append(userToAdd)

	args.update({'allowedusers': hostedUsers})
	args.update({'demands': demands, 'servers': servers, 'users': users, 'permissions': permissions})
	return args


def getarguments_for_manager(request, user):
	'''
	Get permissions to display in view for a manager user.
	'''
	pools = HeimdallUserRole.objects.filter(user__exact=user, type__exact='MANAGER').values_list('pool')
	perimeters = PoolPerimeter.objects.filter(pool__exact=pools)

	servers = []
	for one_perimeter in perimeters:
		servers.append(one_perimeter.server)

	users = []
	user_role = HeimdallUserRole.objects.filter(pool__in=pools)
	for users_roles in user_role:
		users.append(users_roles.user)

	demands = Demands.objects.filter(close_date__isnull=True, server__in=servers)

	permissions = Permission.objects.all()

	args = utils.give_arguments(user, 'Permissions admin')

	hostedUsers = HostedUsers.objects.filter(server__in=servers)

	args.update({'allowedusers': hostedUsers})

	args.update({'demands': demands, 'servers': servers, 'users': users, 'permissions': permissions})
	return args


def add_to_group(request):
	'''
	Add a user to a group (only admin can do this action)
	View Type: Form POST Restricted on Admin
	'''
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			user = User.objects.get(username=request.POST['username'])
			pool = HeimdallPool.objects.get(name=request.POST['poolname'])

			new_userrole = HeimdallUserRole(user=user, pool=pool, type="USER")
			new_userrole.save()

			messages.success(request, 'Pool associated')
			return HttpResponseRedirect(reverse('admin-group-management'))
		else:
			messages.success(request, 'You have not the rights to do this action')
	else:
		messages.success(request, 'You have not the rights to do this action')
	return HttpResponseRedirect(reverse('admin-group-management'))


def manage_user_role(request):
	'''
	Get the users in  pool, simple user and managers.
	View Type: Form GET
	'''
	pool = HeimdallPool.objects.filter(name=request.GET['poolname'])
	userRoles = HeimdallUserRole.objects.filter(pool=pool)

	usersToFilter = []
	notUserSpecialInPool = []
	userSpecialInPool = []
	for userRole in HeimdallUserRole.objects.filter(pool=pool):
		usersToFilter.append(userRole.user.username)
		if not userRole.type == "USER":
			userSpecialInPool.append(userRole.user.username)

	for notSpecialUsers in User.objects.exclude(username__in=userSpecialInPool):
		notUserSpecialInPool.append(notSpecialUsers)

	users = User.objects.exclude(username__in=usersToFilter)
	args = utils.give_arguments(request.user, 'Role management')
	args.update({'userRoles': userRoles, 'users': users, 'not_special_users_in_pool': notUserSpecialInPool, 'userSpecialInPool': userSpecialInPool, 'poolname': request.GET['poolname']})

	return render_to_response('admin/manage_user_role.html', args, context_instance=RequestContext(request))


def manage_group(request):
	'''
	Modify a group
	View Type: Form POST
	'''
	group = Group.objects.get(name=request.POST['groupname'])
	user = User.objects.get(username=request.POST['username'])

	if request.POST['type'] == "add":
		user.groups.add(group)
	else:
		user.groups.remove(group)

	user.save()

	message = 'Group modified'
	messages.success(request, message)
	return HttpResponseRedirect(reverse('admin-group-management'))


def manage_role(request):
	'''
	Modify a pool
	View Type: Form POST
	'''
	if request.method == 'POST':
		user = User.objects.get(username=request.POST['username'])
		pool = HeimdallPool.objects.get(name=request.POST['poolname'])
		if request.POST['type'] == "add":
			userRole = HeimdallUserRole.objects.create(user=user, pool=pool, type='USER')
			userRole.save()
		else:
			userRole = HeimdallUserRole.objects.get(user=user, pool=pool)
			userRole.delete()

		message = 'Group modified'

	else:
		message = 'You have not the rights to do this action'

	messages.success(request, message)
	return HttpResponseRedirect(reverse('admin-group-management'))


def grant_access(request):
	'''
	Grant an access to a server on user.
	View Type: Form POST
	'''
	if request.user.groups.filter(name__in=["heimdall-admin", "heimdall"]):
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

			request_type = request.POST['type']
			if request_type == 'grant':

				message = None

				if not SshKeys.objects.filter(user=user).exists():
					message = 'No RSA saved on database. Contact user to set his RSA key.'
				elif SshKeys.objects.filter(user=user).count() > 1:
					message = 'More than one RSA saved on database. Contact administrator to set his RSA key.'
				else:
					rsa_key = SshKeys.objects.get(user=user)
					err = Controller.addPermission(user, host, request.POST['hostuser'], rsa_key)

					if Demands.objects.filter(user=user, server=host, hostuser=hostuser).exists():
						demand = Demands.objects.get(user=user, server=host, hostuser=hostuser)
						demand.close_date = datetime.today()
						demand.accepted = True
						demand.markAsIgnore = False
						demand.save()

					if err is None:
						if request.POST['username'] != '[[ALL]]':
							message = 'Permission granted on: ' + host.hostname + ' with ' + hostuser + ' (for the user ' + user.username + ')'
						else:
							message = 'All requested permissions granted'
					else:
						message = err.message

				messages.success(request, message)
			else:
				host = Server.objects.get(hostname=request.POST['hostname'])
				demand = Demands.objects.get(user=user, server=host, hostuser=hostuser)
				demand.close_date = datetime.today()
				demand.accepted = False
				demand.markAsIgnore = False
				demand.save()

				message = 'Permission rejected on: ' + host.hostname + ' with ' + hostuser + ' (for the user ' + user.username + ')'
				messages.success(request, message)
	else:
		messages.success(request, 'You have not the rights to do this action')

	return HttpResponseRedirect(reverse('admin-permissions'))


def manage_user_group(request):
	'''
	Manage the users groups' page
	View Type: Form GET
	Accessible by /admin/manage-user-group
	'''
	groups = Group.objects.filter(name=request.GET['groupname'])
	groupUser = User.objects.filter(groups=groups)
	users = User.objects.exclude(username__in=groupUser.values_list('username'))

	args = utils.give_arguments(request.user, 'Group management')
	args.update({'group': groupUser, 'users': users, 'groupname': request.GET['groupname']})
	return render_to_response('admin/user_groups.html', args, context_instance=RequestContext(request))


def manage_groups(request):
	'''
	Manage user accessible pool
	View Type: Form GET
	Accessible by /admin/groups
	'''
	servers = Server.objects.all()

	users = None
	if request.user.groups.filter(name="heimdall-admin"):
		users = User.objects.all()
	else:
		ownRoles = HeimdallUserRole.objects.filter(user=request.user)
		poolUsers = HeimdallUserRole.objects.filter(pool__in=ownRoles.values_list('pool'))
		users = []
		for managed_user in poolUsers:
			if managed_user not in users:
				users.append(managed_user.user)

	userRoles = HeimdallUserRole.objects.all()
	pool = HeimdallPool.objects.all()
	groups = Group.objects.all

	args = utils.give_arguments(request.user, 'Group management')
	args.update({'groups': groups, 'servers': servers, 'users': users, 'roles': pool, 'userRoles': userRoles})

	return render_to_response('admin/groups.html', args, context_instance=RequestContext(request))


def add_group(request):
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			if HeimdallPool.objects.filter(name=request.POST['groupname']).count() == 0:
				pool = HeimdallPool(name=request.POST['groupname'])
				pool.save()
				messages.success(request, "Your data has been saved!")
			else:
				messages.success(request, "Group already exists")

			return HttpResponseRedirect(reverse('admin-group-management'))

	return render_to_response("index.html", context_instance=RequestContext(request))


def perimeter_pool(request):
	'''
	View or Update a perimeter pool. Users / servers (add servers / users to pool / add manager to pool)
	View Type: Form POST / GET
	Accessible by /admin/perimeter-pool
	'''
	if request.user.groups.filter(name="heimdall-admin"):
		servers = Server.objects.all()
		if request.method == 'POST':
			pool = HeimdallPool.objects.get(name=request.POST['poolname'])
			if 'hostname' in request.POST:
				server = Server.objects.get(hostname=request.POST['hostname'])
				role_perimeter = PoolPerimeter.objects.filter(pool=pool)

			if request.POST['action'] == 'add':

				is_allow_to_add = PoolPerimeter.objects.filter(pool=pool, server=server).count() == 0
				if is_allow_to_add:
					new_perimeter = PoolPerimeter(pool=pool, server=server)
					new_perimeter.save()
					role_perimeter = PoolPerimeter.objects.filter(pool=pool)
					messages.success(request, "Group perimeter modified")
					return HttpResponseRedirect(reverse('admin-group-management'))
				else:
					args = utils.give_arguments(request.user, 'Group management')
					messages.success(request, "Server already present in the perimeter")
					return HttpResponseRedirect(reverse('admin-group-management'))

			elif request.POST['action'] == 'remove':
				is_allow_to_remove = PoolPerimeter.objects.filter(pool=pool, server=server).count() == 1
				if is_allow_to_remove:

					perimeter_to_delete = PoolPerimeter.objects.get(pool=pool, server=server)
					perimeter_to_delete.delete()
					args = utils.give_arguments(request.user, 'Group management')
					messages.success(request, "Group perimeter modified")
					return HttpResponseRedirect(reverse('admin-group-management'))
				else:
					args = utils.give_arguments(request.user, 'Group management')
					messages.success(request, "Server not present in the perimeter")
					return HttpResponseRedirect(reverse('admin-group-management'))
			elif request.POST['action'] == 'setmanager':
				user_pool = User.objects.get(username=request.POST['username'])

				if HeimdallUserRole.objects.filter(pool=pool, user=user_pool).exists():
					user_pool_role = HeimdallUserRole.objects.get(pool=pool, user=user_pool)
				else:
					user_pool_role = HeimdallUserRole.objects.create(pool=pool, user=user_pool)
				user_pool_role.type = 'MANAGER'
				user_pool_role.save()

				messages.success(request, "Manager added")
				return HttpResponseRedirect(reverse('admin-group-management'))
			elif request.POST['action'] == 'removemanager':
				user_pool = User.objects.get(username=request.POST['username'])

				if HeimdallUserRole.objects.filter(pool=pool, user=user_pool).exists():
					user_pool_role = HeimdallUserRole.objects.get(pool=pool, user=user_pool)
				else:
					user_pool_role = HeimdallUserRole.objects.create(pool=pool, user=user_pool)
				user_pool_role.type = 'USER'
				user_pool_role.save()

				messages.success(request, "Manager removed")
				return HttpResponseRedirect(reverse('admin-group-management'))

			else:
				messages.success(request, "Action not enabled")
				return HttpResponseRedirect(reverse('admin-group-management'))
		else:
			pool = HeimdallPool.objects.get(name=request.GET['poolname'])
			role_perimeter = PoolPerimeter.objects.filter(pool=pool)

			server_perimeter = []

			for role in role_perimeter:
				server_perimeter.append(role.server)

			managers_in_pool = HeimdallUserRole.objects.filter(pool=pool, type="MANAGER")
			users_not_manager_in_pool = HeimdallUserRole.objects.filter(pool=pool, type="USER")
			args = utils.give_arguments(request.user, 'Group management')
			args.update({'perimeter': role_perimeter, 'servers': servers, 'poolname': request.GET['poolname'], 'server_perimeter': server_perimeter, "managers_in_pool": managers_in_pool, 'users_not_manager_in_pool': users_not_manager_in_pool})
			return render_to_response("admin/pool_perimeter.html", args, context_instance=RequestContext(request))


def register_user(request):
	'''
	Register a new user to Heimdall users.
	Attribute to user the default group heimdall
	View Type: Form POST
	'''
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':

			if 'type' in request.POST:
				if request.POST['type'] == 'update':
					if check_password(request.POST['password'], request.POST['password-confirm']):
						code_return_check = check_params(request.POST['password'], request.POST['username'], request.POST['email'], request.POST['firstname'], request.POST['lastname'])
						if code_return_check == 2:
							group = None
							upd_user = User.objects.get(username=request.POST['username'])
							upd_user.email = request.POST['email']
							upd_user.first_name = request.POST['firstname']
							upd_user.last_name = request.POST['lastname']
							upd_user.set_password(request.POST['password'])
							upd_user.save()
							messages.success(request, "User updated succesfully")
						elif code_return_check == 0:
							messages.success(request, "You need to fill all the blanks fields")
						elif code_return_check == 1:
							messages.success(request, "The username doesn't exists")
						elif code_return_check == 3:
							messages.success(request, "The email you enterred is already associated with another account")
					else:
						messages.success(request, "Password and password confirmation does not match")

					return HttpResponseRedirect(reverse('admin-user'))

			if check_password(request.POST['password'], request.POST['password-confirm']):
				code_return_check = check_params(request.POST['password'], request.POST['username'], request.POST['email'], request.POST['firstname'], request.POST['lastname']) 
				if code_return_check == 1:
					group = None
					if request.POST['role'] == 'ADMIN':
						group = Group.objects.get(name='heimdall-admin')
					else:
						group = Group.objects.get(name='heimdall')

					new_user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password'], first_name=request.POST['firstname'], last_name=request.POST['lastname'])
					new_user.groups.add(group)
					new_user.save()
					messages.success(request, "User created succesfully")
				elif code_return_check == 0:
					messages.success(request, "You need to fill all the blanks fields")
				elif code_return_check == 2:
					messages.success(request, "The username already exists")
				elif code_return_check == 3:
					messages.success(request, "The email you enterred is already associated with another account")

			else:
				messages.success(request, "Password and password confirmation does not match")
	else:

		if check_password(request.POST['password'], request.POST['password-confirm']):
			code_return_check = check_params(request.POST['password'], request.POST['username'], request.POST['email'], request.POST['firstname'], request.POST['lastname'])
			if code_return_check == 2:
				group = None
				upd_user = request.user
				upd_user.email = request.POST['email']
				upd_user.first_name = request.POST['firstname']
				upd_user.last_name = request.POST['lastname']
				upd_user.set_password(request.POST['password'])
				upd_user.save()
			elif code_return_check == 0:
				messages.success(request, "You need to fill all the blanks fields")
			elif code_return_check == 1:
				messages.success(request, "The username doesn't exists")
			elif code_return_check == 3:
				messages.success(request, "The email you enterred is already associated with another account")
		else:
			messages.success(request, "Password and password confirmation does not match")

		return HttpResponseRedirect(reverse('admin-user'))

	return HttpResponseRedirect(reverse('admin-user'))


def check_password(password, password_confirm):
	'''
	Check the password equals to the confirmation password
	'''
	if password == password_confirm:
		return True
	else:
		return False


def check_params(password, username_target, email_target, firstname, lastname):
	'''
	Check if params are valid to save a user infos.
	Rules are: Non-empty username, password, email, firstname, lastname. And Non already exists username and email.
	'''
	output = 0
	if password != "":
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
