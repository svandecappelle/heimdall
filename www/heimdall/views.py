#-*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from heimdall.models import User,Server,Permission
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import User, Group

def index(request):
	return render_to_response('index.html', {'PAGE_TITLE': 'Accueil', 'APP_TITLE' : "Heimdall" }, context_instance=RequestContext(request))
	
def users(request):
	list_users = User.objects.all()
	return render_to_response('users.html', { 'list_users': list_users , 'PAGE_TITLE': 'Utilisateurs', 'APP_TITLE' : "Heimdall"}, context_instance=RequestContext(request))
	
def servers(request):
	list_servers = Server.objects.all()
	return render_to_response('servers.html', { 'list_servers': list_servers , 'PAGE_TITLE': 'Serveurs', 'APP_TITLE' : "Heimdall" }, context_instance=RequestContext(request))
	
def permissions(request):
	list_users = User.objects.all()
	return render_to_response('permissions.html', { 'list_users': list_users , 'PAGE_TITLE': 'Permissions', 'APP_TITLE' : "Heimdall" }, context_instance=RequestContext(request))
	
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