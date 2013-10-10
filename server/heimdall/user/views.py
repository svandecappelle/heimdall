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
from heimdall.models import Server, Permission, Demands, SshKeys, HeimdallPool,HeimdallUserRole, PoolPerimeter
from heimdall.objects import Statistics

# HTTP views
    
# View deposite RSA
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
            key = ''
            
        form = UploadSshKeyForm()

    args = utils.give_arguments(request.user, 'Depot')
    args.update({'documents': docfile, 'form': form, 'key':key})
    return render_to_response('deposite.html', args, context_instance=RequestContext(request))
    
# View demands inbox
def inbox(request):
    pool_role = HeimdallUserRole.objects.filter(user=request.user, type="MANAGER")
    poolPerimeters = PoolPerimeter.objects.filter(pool=pool_role).values_list('server')
    demands = Demands.objects.filter(server=poolPerimeters)
   
    args = utils.give_arguments(request.user, 'Messages')
    args.update({'demands': demands})
    
    return render_to_response('messages.html', args , context_instance=RequestContext(request))

# View Home
def index(request):
    user_count = Group.objects.get(name="heimdall").user_set.all().count()
    user_count += Group.objects.get(name="heimdall-admin").user_set.all().count()
    server_count = Server.objects.all().count()
    keys_count = SshKeys.objects.all().count()
    demands_count = Demands.objects.filter(close_date__isnull=True).all().count()
    
    permissions_count = Permission.objects.all().count()
    stats = Statistics(user_count, server_count, permissions_count, demands_count, keys_count)
    
    args = utils.give_arguments(request.user, 'Acceuil')
    args.update({'stats': stats, 'demands':utils.get_demands_filtered(request.user)})

    return render_to_response('index.html', args, context_instance=RequestContext(request))

# View register user
def register(request):
    args = utils.give_arguments(request.user, 'Register')
    return render_to_response('register.html', args, context_instance=RequestContext(request))

# View users
def users(request):
    list_users = User.objects.all()
    
    args = utils.give_arguments(request.user, 'Utilisateurs')
    args.update({'list_users': list_users})
    
    return render_to_response('users.html', args , context_instance=RequestContext(request))


# HTTPS POST forms

def user_login(request):
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

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('home')


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
                
                if userHost == "":
                    messages.success(request, 'You must write a user host')
                    return HttpResponseRedirect(reverse('servers'))
                
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

