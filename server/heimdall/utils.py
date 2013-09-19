from django.shortcuts import render_to_response
from django.template import RequestContext

def give_arguments(request, page_title):
	return {'PAGE_TITLE': page_title, 'APP_TITLE' : "Heimdall"}

def redirect_to(request, notification, page_name, page):
	args = give_arguments(request, page_name)
	if notification:
		args.update({'NOTIFICATION': notification})
	return render_to_response(page, args, context_instance=RequestContext(request))
