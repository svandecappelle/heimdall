#(r'^heimdall/$', TemplateView.as_view(template_name='index.html'))

from django.conf.urls import patterns, url

from heimdall import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^home$', views.index, name='index'),
    url(r'^users$', views.users, name='users'),
    url(r'^servers$', views.servers, name='servers'),
    url(r'^permissions$', views.permissions, name='permissions'),
    url(r'^deposite$', views.deposite, name='deposite'),
    url(r'^connect$', views.connect, name='connect'),
    url(r'^connect$', 'django.contrib.auth.views.login', {'template_name': 'heimdall/connect.html'}),
    url(r'^login$', views.mylogin),
    url(r'^logout$', views.mylogout),
    url(r'^require_access$', views.require_access, name='require_access'),
    url(r'^register$', views.register, name='register'),
    url(r'^register_action$', views.register_action, name='register_action'),
)
