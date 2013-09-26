from django.shortcuts import render_to_response
from django.template import RequestContext

from heimdall.models import Demands, UserRoles, RolePerimeter

def give_arguments(user, page_title):
	return {'PAGE_TITLE': page_title, 'APP_TITLE' : "Heimdall", 'inbox_demands_count':get_demands_filtered(user).count}

# utils
def get_demands_filtered(user_filter):
	userRoles = UserRoles.objects.filter(user=user_filter).values_list('role')
	rolePerimeters = RolePerimeter.objects.filter(roles=userRoles).values_list('server')
	demands = Demands.objects.filter(server=rolePerimeters,close_date__isnull=True)
	return demands

def handler404(request):
	#args = give_arguments(request.user, 'Not found')
	return render_to_response('errors/404.html', {'PAGE_TITLE': "404", 'APP_TITLE' : "Heimdall"}, context_instance=RequestContext(request))

def handler500(request):
	#args = give_arguments(request.user, 'Internal error')
	return render_to_response('errors/500.html', {'PAGE_TITLE': "500", 'APP_TITLE' : "Heimdall"}, context_instance=RequestContext(request))
