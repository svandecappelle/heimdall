#-*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from heimdall.models import Server,Permission, Demands
from heimdall.objects import Statistics
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import User, Group
from datetime import date

def index(request):
	user_count = Group.objects.get(name="heimdall").user_set.all().count()
	server_count = Server.objects.all().count()
	demands_count = Demands.objects.filter(close_date__isnull=True).all().count()
	
	permissions_count = Permission.objects.all().count()
	stats = Statistics(user_count,server_count,permissions_count,demands_count)
	
	demands = Demands.objects.filter(close_date__isnull=True).all()
	
	return render_to_response('index.html', {'stats': stats, 'demands':demands, 'PAGE_TITLE': 'Accueil', 'APP_TITLE' : "Heimdall" }, context_instance=RequestContext(request))
	
def users(request):
	list_users = User.objects.all()
	return render_to_response('users.html', { 'list_users': list_users , 'PAGE_TITLE': 'Utilisateurs', 'APP_TITLE' : "Heimdall"}, context_instance=RequestContext(request))
	
def servers(request):
	list_servers = Server.objects.all()
	return render_to_response('servers.html', { 'list_servers': list_servers , 'PAGE_TITLE': 'Serveurs', 'APP_TITLE' : "Heimdall" }, context_instance=RequestContext(request))
	
def permissions(request):
	all_permissions = Permission.objects.all()
	users_in_group = Group.objects.get(name="heimdall").user_set.all()
	users_in_group_admin = Group.objects.get(name="heimdall-admin").user_set.all()
	
	userConnected = request.user
	if userConnected.is_authenticated:
		if userConnected.groups.filter(name="heimdall-admin"):
			return render_to_response('permissions.html', { 'permissions': convertToIterable(all_permissions) , 'PAGE_TITLE': 'Permissions', 'APP_TITLE' : "Heimdall" }, context_instance=RequestContext(request))
		elif userConnected.groups.filter(name="heimdall"):
			permissions_visible = Permission.objects.get(user=userConnected)
			return render_to_response('permissions.html', { 'permissions': convertToIterable(permissions_visible) , 'PAGE_TITLE': 'Permissions', 'APP_TITLE' : "Heimdall" }, context_instance=RequestContext(request))
		else:
			return render_to_response('permissions.html', {'PAGE_TITLE': 'Permissions', 'APP_TITLE' : "Heimdall" }, context_instance=RequestContext(request))

def convertToIterable(permissions_visible):
	try:
		some_object_iterator = iter(permissions_visible)
		permissions_visible_to_return = permissions_visible
	except TypeError, te:
		permissions_visible_to_return = [1]
		permissions_visible_to_return[0] = permissions_visible
	
	return permissions_visible_to_return

def deposite(request):
	list_users = User.objects.all()
	return render_to_response('deposite.html', { 'list_users': list_users , 'PAGE_TITLE': 'Depot', 'APP_TITLE' : "Heimdall" }, context_instance=RequestContext(request))
	
def connect(request):
	return render_to_response('connect.html', {'PAGE_TITLE': 'Connect', 'APP_TITLE' : "Heimdall" }, context_instance=RequestContext(request))
	

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
				return HttpResponseRedirect('home')
			else:
				#disabled account
				return direct_to_template(request, 'inactive_account.html')
		else:
			# invalid login
			return HttpResponseRedirect('home')
	else:
		return HttpResponseRedirect('home')
      

def mylogout(request):
	logout(request)
	return HttpResponseRedirect('home')
	
	
	user = models.ForeignKey(User)
	server = models.ForeignKey(Server)
	hostuser = models.CharField(max_length=50)
	priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
	comments = models.CharField(max_length=4000, null=True, blank=True)
	cdate = models.DateField()
	close_date = models.DateField(null=True, blank=True)
	
	
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
				demand = Demands(user=userConnected,server=serverHost,hostuser=userHost,priority=priority,comments=comments,cdate=cdate)
				demand.save()
				
				list_servers = Server.objects.all()
				return render_to_response('servers.html', { 'list_servers': list_servers , 'PAGE_TITLE': 'Serveurs', 'APP_TITLE' : "Heimdall", 'ACTION':'DONE' }, context_instance=RequestContext(request))
				
		else:
			return HttpResponseRedirect('home')
	else:
		return HttpResponseRedirect('home')
