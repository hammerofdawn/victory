from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),

    url(r'^dashboard/$', views.dashboard, name='dashboard'),

    url(r'^users/$', views.users, name='users'),
    url(r'^users/(?P<user_pk>[0-9]+)/$', views.user, name='user'),

    url(r'^teams/$', views.teams, name='teams'),
    url(r'^teams/(?P<team_id>[0-9]+)/$', views.team, name='team'),
]

# url(r'^$', views.index, name='index'),
