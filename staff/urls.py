from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^login/$', views.login, name='login'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^register/$', views.register, name='register'),
	url(r'^register/image/$', views.registerimage, name='registerimage'),
	url(r'^users/$', views.users, name='users'),
	url(r'^users/(?P<user_pk>[0-9]+)/$', views.user, name='user'),
	url(r'^users/(?P<user_pk>[0-9]+)/settings/$', views.usersettings, name='usersettings'),
	url(r'^teams/$', views.teams, name='teams'),
	url(r'^teams/(?P<team_pk>[0-9]+)/$', views.team, name='team'),
	url(r'^apply/$', views.apply, name='apply'),
]
