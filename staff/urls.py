from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.welcome, name='welcome'),
    url(r'^home/$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^users/$', views.users, name='users'),
    url(r'^users/(?P<user_pk>[0-9]+)/$', views.user, name='user'),
    url(r'^teams/$', views.teams, name='teams'),
    url(r'^teams/(?P<team_pk>[0-9]+)/$', views.team, name='team'),
]
