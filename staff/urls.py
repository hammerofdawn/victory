from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^login/$', views.login, name='login'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^register/$', views.register, name='register'),
	url(r'^users/$', views.users, name='users'),
	url(r'^message/$', views.webmessage, name='webmessage'),
	url(r'^users/(?P<user_pk>[0-9]+)/$', views.user, name='user'),
	url(r'^users/(?P<user_pk>[0-9]+)/settings/$', views.usersettings, name='usersettings'),
	url(r'^users/(?P<user_pk>[0-9]+)/settings/profile/$', views.userprofileupdate, name='userprofileupdate'),
	url(r'^users/(?P<user_pk>[0-9]+)/settings/social/$', views.usersociallinks, name='usersociallinks'),
	url(r'^users/(?P<user_pk>[0-9]+)/settings/avatar/$', views.useravatar, name='useravatar'),
	url(r'^users/(?P<user_pk>[0-9]+)/settings/background/$', views.userbackground, name='userbackground'),
	url(r'^users/(?P<user_pk>[0-9]+)/settings/change_password$', views.user_change_password, name='user_change_password'),
	url(r'^teams/$', views.teams, name='teams'),
	url(r'^teams/(?P<team_pk>[0-9]+)/$', views.team, name='team'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/$', views.teamsettings_general, name='teamsettings_general'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/message$', views.teamsettings_message, name='teamsettings_message'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/logo/$', views.teamsettings_logo, name='teamsettings_logo'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/background/$', views.teamsettings_background, name='teamsettings_background'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/description/$', views.teamsettings_description, name='teamsettings_description'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/members/$', views.teamsettings_members, name='teamsettings_members'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/members/add/$', views.teamsettings_members_add, name='teamsettings_members_add'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/members/delete/$', views.teamsettings_members_delete, name='teamsettings_members_delete'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/applications/$', views.teamsettings_applications, name='teamsettings_applications'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/applications/accepted/$', views.teamsettings_accept_applications, name='teamsettings_accept_applications'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/applications/needinfo/$', views.teamsettings_needinfo_applications, name='teamsettings_needinfo_applications'),
	url(r'^teams/(?P<team_pk>[0-9]+)/settings/applications/refuse/$', views.teamsettings_refuse_applications, name='teamsettings_refuse_applications'),
	url(r'^apply/$', views.apply, name='apply'),
	url(r'^apply/sent/$', views.applysent, name='applysent'),
	url(r'^apply/accept/$', views.useraccept, name='useraccept'),
	url(r'^apply/delete/$', views.applydelete, name='applydelete'),
	url(r'^contact/$', views.contact, name='contact'),
	## PASSWORD RESET
	url(r'^password_reset/$', auth_views.password_reset, {
		'template_name'			  : 'reset/password_reset_form.html',
		'subject_template_name'	  : 'email/password_reset_subject.txt',
		'html_email_template_name': 'email/password_reset_email.html',
		'from_email'			  : 'info@victory.genki.dk'
		}, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done,{'template_name': 'reset/password_reset_done.html'}, name='password_reset_done'),
	url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,{'template_name': 'reset/password_reset_confirm.html'}, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete,{'template_name': 'reset/password_reset_complete.html'}, name='password_reset_complete'),
]
