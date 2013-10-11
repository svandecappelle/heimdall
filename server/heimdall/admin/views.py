# -*- coding: utf-8 -*-
# Create your views here.
from datetime import date

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from heimdall import utils
from heimdall.bastion.runner import Controller
from heimdall.models import Server, Demands, SshKeys, HeimdallPool, PoolPerimeter, HeimdallUserRole, Permission


#Installation
def install(request):
	if not Group.objects.filter(name='heimdall').exists():
		user_group = Group.objects.create(name='heimdall')
		user_group.save()
		print "heimdall group created"

	
	if not Group.objects.filter(name='heimdall-admin').exists():
		group = Group.objects.create(name='heimdall-admin')
		group.save()
		print "admin group created"
	else:
		group = Group.objects.get(name='heimdall-admin')
		
	if not User.objects.filter(username='heimdall').exists():
		new_user = User.objects.create_user(username="heimdall",password="heimdall")
		new_user.groups.add(group)
		new_user.save()
		print "admin user created"

	messages.success(request, 'Installation successfull. You can connect with heimdall')
	return render_to_response('index.html', context_instance=RequestContext(request))



def user(request):
	args = utils.give_arguments(request.user, 'Users admin')
	if request.user.groups.filter(name="heimdall-admin"):
		users = list(Group.objects.get(name="heimdall").user_set.all())
		admin_users = Group.objects.get(name="heimdall-admin").user_set.all()
		
		for user in admin_users:
			if user not in users:
				users.append(user)
		
		args.update({'list_users': users})
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
			
			message = None
			
			if SshKeys.objects.filter(user=user).count == 0:
				message = 'No RSA saved on database. Contact user to set his RSA key.'
			elif SshKeys.objects.filter(user=user).count > 1:
				message = 'More than one RSA saved on database. Contact administrator to set his RSA key.'
			else:
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
				
				if Server.objects.filter(hostname=request.POST['hostname']).exists():
					server = Server.objects.get(hostname=request.POST['hostname'])
					messages.success(request, 'Server updated')
				
				else:
					server = Server(hostname=request.POST['hostname'], description= request.POST['description'], port=request.POST['port'])
					messages.success(request, 'Server created')
				
				server.save()
			
				return HttpResponseRedirect(reverse('servers'))

			messages.success(request, 'Form datas in errors. Check your parameters.')
			return HttpResponseRedirect(reverse('create-server'))
		else:
			if 'hostname' in request.GET:
				host = Server.objects.get(hostname=request.GET['hostname'])
				args = utils.give_arguments(request.user, 'Create server')
				
				args.update({'hostname' : host.hostname, 'description' : host.description, 'port': host.port})
				return render_to_response('admin/create_server.html', args, context_instance=RequestContext(request))
			
			
			return render_to_response('admin/create_server.html', context_instance=RequestContext(request))

	else:
		messages.success(request, 'You have not the rights to do this action')
	return HttpResponseRedirect(reverse('servers'))

def permissions(request):
	if request.user.groups.filter(name="heimdall-admin"):
		args = getarguments_for_admin(request.user)
	else:
		args = getarguments_for_manager(request.user)

	return render_to_response('admin/permissions.html', args, context_instance=RequestContext(request))

def getarguments_for_admin(user):
	servers = Server.objects.all()
	users = User.objects.all()
	demands = Demands.objects.all();
	permissions = Permission.objects.all()
	args = utils.give_arguments(user, 'Permissions admin')
	args.update({'demands' : demands, 'servers': servers, 'users': users, 'permissions' : permissions})
	return args

def getarguments_for_manager(user):
	pools = HeimdallUserRole.objects.filter(user=user)
	perimeters = PoolPerimeter.objects.filter(pool = pools)

	servers=[]
	for one_perimeter in perimeters:	
		servers.append(one_perimeter.server)

	users=[]
	for one_role_pool in pools:
		user_role = HeimdallUserRole.objects.filter(pool=one_role_pool.pool)
		for users_roles in user_role:
			users.append(users_roles.user)
	
	demands = Demands.objects.filter(close_date__isnull=True, user__in= users, server__in =servers)
	for filtered_demands in demands:
		
		print filtered_demands
	
	
	#users = User.objects.all()
	permissions = Permission.objects.all()
	
	args = utils.give_arguments(user, 'Permissions admin')
	args.update({'demands' : demands, 'servers': servers, 'users': users, 'permissions' : permissions})
	return args

def add_to_group(request):
	if request.user.groups.filter(name="heimdall-admin"):
		if request.method == 'POST':
			user = User.objects.get(username=request.POST['username'])
			pool = HeimdallPool.objects.get(name=request.POST['poolname'])
			
			new_userrole = HeimdallUserRole(user=user, pool=pool, type="USERS")
			new_userrole.save()
			
			messages.success(request, 'Role associated')
			return HttpResponseRedirect(reverse('admin-group-management'))
		else:
			messages.success(request, 'You have not the rights to do this action')
	else:
		messages.success(request, 'You have not the rights to do this action')
		
	return HttpResponseRedirect(reverse('admin-group-management'))

def manage_user_role(request):
	pool = HeimdallPool.objects.filter(name=request.GET['poolname'])	
	userRoles = HeimdallUserRole.objects.filter(pool=pool)
	usersToFilter = []
	for userRole in HeimdallUserRole.objects.filter(pool=pool):
		print (userRole.user)
		usersToFilter.append(userRole.user.username)
		
	users = User.objects.exclude(username__in=usersToFilter)
	print (users)
	args = utils.give_arguments(request.user, 'Role management')
	args.update({'userRoles' : userRoles , 'users':users, 'poolname' : request.GET['poolname']})	
	
	return render_to_response('admin/manage_user_role.html',args, context_instance=RequestContext(request))

def manage_group(request):
	
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
	if request.user.groups.filter(name="heimdall-admin"):
		user = User.objects.get(username=request.POST['username'])
		pool = HeimdallPool.objects.get(name=request.POST['poolname'])
		
		if request.POST['type'] == "add":
			HeimdallUserRole.objects.create(user=user,pool=pool)
		else:
			userRole = HeimdallUserRole.objects.get(user=user,pool=pool)
			userRole.delete()
		
		message = 'Group modified'
		
	else:
		message = 'You have not the rights to do this action'
		
	messages.success(request, message)
	return HttpResponseRedirect(reverse('admin-group-management'))
	

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
			
			request_type = request.POST['type']
			if request_type == 'grant':
				
				message = None
				
				if SshKeys.objects.filter(user=user).count == 0:
					message = 'No RSA saved on database. Contact user to set his RSA key.'
				elif SshKeys.objects.filter(user=user).count > 1:
					message = 'More than one RSA saved on database. Contact administrator to set his RSA key.'
				else:
					rsa_key = SshKeys.objects.get(user=user)
					Controller.addPermission(user, host, request.POST['hostuser'], rsa_key)
					demand = Demands.objects.get(user=user,server=host,hostuser=hostuser)
					demand.close_date=date.today()
					demand.save()
				
				if request.POST['username'] != '[[ALL]]':
					message = 'Permission granted on: ' + host.hostname + ' with ' + hostuser + ' (for the user ' + user.username + ')' 
					messages.success(request, message)
				else:
					messages.success(request, 'All requested permissions granted')
			else:
				host = Server.objects.get(hostname=request.POST['hostname'])
				demand = Demands.objects.get(user=user,server=host,hostuser=hostuser)
				demand.close_date=date.today()
				demand.save()
				
				message = 'Permission rejected on: ' + host.hostname + ' with ' + hostuser + ' (for the user ' + user.username + ')' 
				messages.success(request, message)
	else:
		messages.success(request, 'You have not the rights to do this action')

	return HttpResponseRedirect(reverse('admin-permissions'))

def manage_user_group(request):
	groups = Group.objects.filter(name=request.GET['groupname'])
	groupUser = User.objects.filter(groups=groups)	
	users = User.objects.exclude(username__in=groupUser.values_list('username'))
	
	args = utils.give_arguments(request.user, 'Group management')
	args.update({'group': groupUser, 'users':users,'groupname' : request.GET['groupname']})
	
	return render_to_response('admin/user_groups.html', args, context_instance=RequestContext(request))

def manage_groups(request):
	servers = Server.objects.all()	
	users = User.objects.all()
	
	userRoles = HeimdallUserRole.objects.all()
	pool = HeimdallPool.objects.all()
	groups = Group.objects.all
	
	args = utils.give_arguments(request.user, 'Group management')
	args.update({'groups' : groups, 'servers': servers, 'users': users, 'roles': pool, 'userRoles' : userRoles})	
	
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
	if request.user.groups.filter(name="heimdall-admin"):
		servers = Server.objects.all()
		if request.method == 'POST':
			pool = HeimdallPool.objects.get(name=request.POST['poolname'])
			if 'hostname' in request.POST:
				server = Server.objects.get(hostname=request.POST['hostname'])
				role_perimeter = PoolPerimeter.objects.filter(pool=HeimdallPool.objects.get(name=request.POST['poolname']))
			
			if request.POST['action'] == 'add':
				
				is_allow_to_add = PoolPerimeter.objects.filter(pool=pool, server=server).count() == 0
				print is_allow_to_add
				if is_allow_to_add:
					new_perimeter = PoolPerimeter(pool=pool, server=server)
					new_perimeter.save()
					role_perimeter = PoolPerimeter.objects.filter(pool=HeimdallPool.objects.get(name=request.POST['poolname ']))
					messages.success(request, "Group perimeter modified")
					return HttpResponseRedirect(reverse('admin-group-management'))
				else:                                                                                                    
					args = utils.give_arguments(request.user, 'Group management')
					messages.success(request, "Server already present in the perimeter")
					return HttpResponseRedirect(reverse('admin-group-management'))
					
			elif request.POST['action'] == 'remove':
				is_allow_to_remove = HeimdallPool.objects.filter(pool=pool, server=server).count() == 1
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
				user_pool_role = HeimdallUserRole.objects.get(pool=pool,user=user_pool)
				user_pool_role.type='MANAGER'
				user_pool_role.save()
				
				messages.success(request, "Manager added")
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
			
			managers_in_pool = HeimdallUserRole.objects.filter(pool=pool,type="MANAGER")
			users_not_manager_in_pool = HeimdallUserRole.objects.filter(pool=pool, type="USER")
			args = utils.give_arguments(request.user, 'Group management')
			args.update({'perimeter': role_perimeter, 'servers' : servers, 'poolname': request.GET['poolname'], 'server_perimeter':server_perimeter ,"managers_in_pool" : managers_in_pool , 'users_not_manager_in_pool' : users_not_manager_in_pool})	
			return render_to_response("admin/pool_perimeter.html", args, context_instance=RequestContext(request))

def register_user(request):
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
