from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate as auth_authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import EmailAndSmsMessages, ExtendedUser, Article, UnauthenticatedSession, Team, DriversLicenceCategories, TeamApplication, TeamMembership, Language, TShirt
from .forms import UpdateSociallinksForm, UpdateTeambackground, UpdateTeamlogo, UpdateProfileBackground, SignUpForm, UpdateProfileForm, SendApplication, FeedbackSupportForm, TeamSettings_GeneralForm, TeamSettings_DescriptionForm, TeamSettings_acceptForm, TeamSettings_needinfo_andrefuseForm, TeamSettings_AddForm, UpdateProfileAvatar
from uuid import uuid4
from random import randint
import requests
import os
from requests_oauthlib import OAuth1Session

# Create your views here.

def index(request):
	if request.user.is_authenticated():
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		articles = Article.objects.all().order_by('-created')
		feedback = FeedbackSupportForm()
		context = {
			'logged_in_user': logged_in_user,
			'articles': articles,
			'feedback': feedback,
		}

		return render(request, 'dashboard.html', context)
	else:
		return render(request, 'welcome.html')

def teams(request):
	teams = Team.objects.all().order_by('name')
	feedback = FeedbackSupportForm()
	context = {
		'teams': teams,
		'feedback': feedback,
	}
	if request.user.is_authenticated():
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		context['logged_in_user'] = logged_in_user
	return render(request, 'teams.html', context)

def login(request):
	if request.user.is_authenticated():
		return redirect('index')

	if request.method != 'POST': # We only support login via POST
		feedback = FeedbackSupportForm()
		return render(request, 'login.html', {'feedback': feedback,})

	token = request.POST.get('token', None)
	username = request.POST.get('username', None)
	password = request.POST.get('password', None)

	if token is not None:
		otpdigit1 = request.POST.get('otpdigit1', '')
		otpdigit2 = request.POST.get('otpdigit2', '')
		otpdigit3 = request.POST.get('otpdigit3', '')
		otpdigit4 = request.POST.get('otpdigit4', '')

		otp = otpdigit1 + otpdigit2 + otpdigit3 + otpdigit4
		if len(otp) != 4:
			return render(request, "2ndfactor.html", {'error': True}) # Return because of invalid otp
		try:
			ua = UnauthenticatedSession.objects.get(token=str(token))
		except Exception as e:
			return render(request, '2ndfactor.html', {
				'error': "Your token wasn't found. Please authenticate using an alternate method"
			})

		if ua.guesses_left <= 0: # less to be sure no bugs or funny business
			messages.error(request, "Code has been entered incorrectly too many times. Please try again or contact us.")
			return render(request, "login.html", {})

		if ua.guesses_left > 0:
			if ua.successful:
				return render(request, "2ndfactor.html", {
					'error': "Token has already been used.",
				})

			if otp != ua.otp:
				ua.guesses_left -= 1
				ua.save()
				return render(request, "2ndfactor.html", {'token': token})

			ua.successful = True
			ua.save()

			auth_login(request, ua.user)
			return redirect('index')

	elif username and password:
		user = auth_authenticate(request, username=username, password=password)

		if user == None: # Who you tryna login as
			feedback = FeedbackSupportForm()
			return render(request, "login.html", {'invalid': True, 'feedback': feedback, })

		token = str(uuid4())
		otp = str(randint(1111, 9999))

		gwapi = OAuth1Session('OCBzbvY1b1FCQpTzEa4_131V', client_secret='g^oqsxSClJ(A@-Yttu-D6.C5lB6YdeBVz&LJ6E3W')

		req = {
			'message': 'Victory login code:\n{} {} {} {}'.format(otp[0:1], otp[1:2], otp[2:3], otp[3:4]),
			'recipients': [{'msisdn': user.extendeduser.phone_number[1:]}],
			'destaddr': 'DISPLAY',
			'sender': 'VICTORY',
		}
		res = gwapi.post('https://gatewayapi.com/rest/mtsms', json=req)
		res.raise_for_status()

		us = UnauthenticatedSession()
		us.user = user
		us.token = token
		us.otp = otp

		us.save()
		feedback = FeedbackSupportForm()
		return render(request, "2ndfactor.html", {'token': token, 'feedback': feedback,})
	else:
		feedback = FeedbackSupportForm()
		return render(request, "login.html", {'feedback': feedback,})

def logout(request):
	auth_logout(request)
	return redirect('index')

def register(request):
	if request.method != 'POST':
		form = SignUpForm()
		feedback = FeedbackSupportForm()
		return render(request, 'register.html', {'form': form, 'feedback': feedback,})

	form = SignUpForm(request.POST)
	if not form.is_valid():
		feedback = FeedbackSupportForm()
		return render(request, 'register.html', {'form': form, 'feedback': feedback})

	user = form.save()
	user.refresh_from_db()  # load the profile instance created by the signal
	user.extendeduser.postal_code = form.cleaned_data.get('postal_code')
	user.extendeduser.phone_number = form.cleaned_data.get('phone_number')
	user.extendeduser.nickname = form.cleaned_data.get('username')
	user.save()
	raw_password = form.cleaned_data.get('password1')
	user = auth_authenticate(username=user.username, password=raw_password)
	auth_login(request, user)
	return redirect('index')

def contact(request):
	if request.method == 'POST':
		form = FeedbackSupportForm(request.POST)
		if form.is_valid():
			try:
				user_mail = form.cleaned_data['email']
				first_name = form.cleaned_data['first_name']
				last_name = form.cleaned_data['last_name']
				message = form.cleaned_data['message']
				subject = "Message from contact form. Victory"
				from_email = 'info@victory.genki.dk'
				context = {
					'user_mail'  : user_mail,
					'first_name' : first_name,
					'last_name'	 : last_name,
					'message'	 : message,
				}
				text_content = render_to_string('email/contactmessage.html', context)
				msg = EmailMultiAlternatives(subject, text_content, from_email, ['melonendk@gmail.com', 'deni@radera.net'])
				msg.content_subtype = "html"  # Main content is now text/html
				msg.send()
			except BadHeaderError:
				return HttpResponse('Invalid header found.')
			messages.success(request, "Sweet! Your message has been send! Please allow up to 24 hours for response time.")
			return redirect('index')
	else:
		return redirect('index')

@login_required
def users(request):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	users = User.objects.all().order_by('username')
	feedback = FeedbackSupportForm()
	context = {
		'logged_in_user': logged_in_user,
		'users': users,
		'feedback': feedback,
	}

	return render(request, 'users.html', context)

@login_required
def user(request, user_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_user = get_object_or_404(User, pk=user_pk)
	feedback = FeedbackSupportForm()
	try:
		memberof = TeamMembership.objects.get(user=user_pk)
	except TeamMembership.DoesNotExist:
		memberof = None
	
	context = {
		'logged_in_user': logged_in_user,
		'requested_user': requested_user,
		'editable': True, # Has to do actual permission logic.
		'feedback': feedback,
	}
	if memberof:
		context['memberof'] = memberof
	

	return render(request, 'user/profile.html', context)

@login_required
def usersettings(request, user_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_user = get_object_or_404(User, pk=user_pk)
	driverslicence = DriversLicenceCategories.objects.all()
	language = Language.objects.all()
	tshirt = TShirt.objects.all()
	form = UpdateProfileForm(instance=request.user)
	social = UpdateSociallinksForm(instance=request.user)
	feedback = FeedbackSupportForm()
	password = PasswordChangeForm(request.user)
	context = {
		'logged_in_user': logged_in_user,
		'requested_user': requested_user,
		'driverslicence': driverslicence,
		'language'		: language,
		'tshirt'		: tshirt,
		'form'			: form,
		'social'		: social,
		'feedback'		: feedback,
		'password'		: password,
	}
	return render(request, 'user/settings.html', context)

@login_required
def userprofileupdate(request, user_pk):
	if request.method == 'POST':
		form = UpdateProfileForm(request.POST, instance=request.user)
		logged_in_user = get_object_or_404(User, pk=request.user.pk)

		if logged_in_user.username != request.POST['username']:
			users = User.objects.filter(username=request.POST['username']).count()
			if users > 0:
				messages.info(request, "Username already taken.")
				return redirect('usersettings', user_pk=request.user.pk)

		if form.is_valid():
			user = form.save()
			user.refresh_from_db()  # load the profile instance created by the signal
			user.extendeduser.nickname = form.cleaned_data.get('username')
			user.extendeduser.postal_code = form.cleaned_data.get('postal_code')
			user.extendeduser.phone_number = form.cleaned_data.get('phone_number')
			user.extendeduser.phone_number_show = form.cleaned_data.get('phone_number_show')
			user.extendeduser.emergency_number = form.cleaned_data.get('emergency_number')
			user.extendeduser.birthdate = form.cleaned_data.get('birthdate')
			user.extendeduser.languages = form.cleaned_data.get('languages')
			user.extendeduser.drivers_licence = form.cleaned_data.get('drivers_licence')
			user.extendeduser.tshirt = form.cleaned_data.get('tshirt')
			user.extendeduser.special_considerations = form.cleaned_data.get('special_considerations')
			user.save()
			user.extendeduser.save()
			messages.success(request, "Your profile has been updated!")
			return redirect('usersettings', user_pk=request.user.pk)
	messages.success(request, "Please update your profile before going here.")
	return redirect('usersettings', user_pk=request.user.pk)

@login_required
def usersociallinks(request, user_pk):
	if request.method == 'POST':
		form = UpdateSociallinksForm(request.POST, instance=request.user)
		if form.is_valid():
			user = form.save()
			user.refresh_from_db()  # load the profile instance created by the signal
			user.extendeduser.facebook_link = form.cleaned_data.get('facebook_link')
			user.extendeduser.twitter_link = form.cleaned_data.get('twitter_link')
			user.extendeduser.soundcloud_link = form.cleaned_data.get('soundcloud_link')
			user.extendeduser.youtube_link = form.cleaned_data.get('youtube_link')
			user.save()
			user.extendeduser.save()
			messages.success(request, "Your Social links has been updated!")
			return redirect('usersettings', user_pk=request.user.pk)
		else:
			messages.success(request, "Need's to be a URL")
			return redirect('usersettings', user_pk=request.user.pk)
	messages.success(request, "Please update your profile before going here.")
	return redirect('usersettings', user_pk=request.user.pk)

@login_required
def useravatar(request, user_pk):
	if request.method == 'POST':
		form = UpdateProfileAvatar(request.POST, request.FILES, instance=request.user)
		if form.is_valid():
			print(request.POST)
			user = form.save(commit=False)
			user.extendeduser.avatar = request.FILES['avatar']
			user.save()
			messages.success(request, 'Your avatar was successfully Uploaded!')
			return redirect('useravatar', user_pk=request.user.pk)
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_user = get_object_or_404(User, pk=user_pk)
	feedback = FeedbackSupportForm()
	password = PasswordChangeForm(request.user)
	avatar = UpdateProfileAvatar(instance=request.user)
	background = UpdateProfileBackground(instance=request.user)
	context = {
		'avatar'		: avatar,
		'background'	: background,
		'logged_in_user': logged_in_user,
		'requested_user': requested_user,
		'feedback'		: feedback,
		'password'		: password,
	}
	return render(request, 'user/avatar.html', context)

@login_required
def userbackground(request, user_pk):
	if request.method == 'POST':
		form = UpdateProfileBackground(request.POST, request.FILES, instance=request.user)
		if form.is_valid():
			user = form.save(commit=False)
			user.extendeduser.background = request.FILES['background']
			user.save()
			messages.success(request, 'Your background was successfully Uploaded!')
			return redirect('useravatar', user_pk=request.user.pk)

	messages.error(request, 'Error please select the image u want to upload.')
	return redirect('useravatar', user_pk=request.user.pk)

def user_change_password(request, user_pk):
	if request.method != 'POST':
		redirect('usersettings', user_pk=request.user.pk)
	form = PasswordChangeForm(request.user, request.POST)

	if form.is_valid():
		user = form.save()
		update_session_auth_hash(request, user)  # Important!
		messages.success(request, 'Your password was successfully updated!')
		return redirect('usersettings', user_pk=request.user.pk)
	else:
		messages.error(request, 'Please correct the error below.')
		return redirect('usersettings', user_pk=request.user.pk)

def team(request, team_pk):
	requested_team = get_object_or_404(Team, pk=team_pk)
	feedback = FeedbackSupportForm()
	context = {
		'requested_team': requested_team,
		'feedback': feedback,
	}

	if requested_team.multiple_teamleaders:
		context["multiple_teamleaders"] = True

	if request.user.is_authenticated():
		if requested_team.members.all().count() > 0:
			context['teamhasmembers'] = True
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		context['logged_in_user'] = logged_in_user
		for member in requested_team.teammembership_set.all():
			if member.user.pk == request.user.pk and member.leader:
				context['caneditteam'] = True
				break
	return render(request, 'team/team.html', context)

@login_required
def teamsettings_general(request, team_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_team = get_object_or_404(Team, pk=team_pk)
	if request.method == 'POST':
		for member in requested_team.teammembership_set.all().order_by('-leader'):
			if member.user.pk == request.user.pk and member.leader:
				form = TeamSettings_GeneralForm(request.POST, instance=requested_team)
				if form.is_valid():
					form.save()
					messages.success(request, "The team has been updated!")
					return redirect('teamsettings_general', team_pk=team_pk)
	for member in requested_team.teammembership_set.all().order_by('-leader'):
		if member.user.pk == request.user.pk and member.leader:
			feedback = FeedbackSupportForm()
			form = TeamSettings_GeneralForm(instance=requested_team)
			logo = UpdateTeamlogo(request.POST, request.FILES, instance=requested_team)
			background = UpdateTeambackground(request.POST, request.FILES, instance=requested_team)
			context = {
				'requested_team': requested_team,
				'feedback': feedback,
				'form' : form,
				'logo' : logo,
				'background': background,
				'logged_in_user': logged_in_user,
			}
			return render(request, 'team/settings.html', context)
	return redirect('team', team_pk)

def webmessage(request):
	token_id = request.GET.get('t', '')
	user_pk = request.GET.get('u', '')
	if token_id and user_pk:
		message = get_object_or_404(EmailAndSmsMessages, token=token_id)
		user = get_object_or_404(User, pk=user_pk)
		team = message.team
		if message.members.all().filter(user=user.pk):
			context = {
				'user'   : user,
				'team'   : team,
				'message': message,
			}
			return render(request, 'email/teamlmessageweb.html', context)
		else:
			raise Http404
	else:
		raise Http404

@login_required
def teamsettings_message(request, team_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_team = get_object_or_404(Team, pk=team_pk)
	memberships = requested_team.teammembership_set.all().order_by('-leader')
	if request.method == 'POST':
		for member in memberships:
			if member.user.pk == request.user.pk and member.leader:
				typemessage = request.POST['typemessage']
				people = request.POST.getlist('people[]')
				subject = request.POST['subject']
				message = request.POST['message']
				countsms = 0
				countemail = 0
				if typemessage and people and subject and message:
					if any("ALL" in s for s in people):
						token = str(uuid4().hex)
						emailsmsdata = EmailAndSmsMessages()
						emailsmsdata.token = token
						emailsmsdata.msgtype = typemessage
						emailsmsdata.team = requested_team
						emailsmsdata.subject = subject
						emailsmsdata.message = message
						emailsmsdata.save()
						for member in memberships:
							emailsmsdata.members.add(member)
							if request.POST['typemessage'] == "email" or request.POST['typemessage'] == "both":
								from_email, to = 'info@victory.genki.dk', member.user.email
								messagelink = '?u='+str(member.user.id)+'&t='+str(emailsmsdata.token)
								context = {
									'weblink'	: messagelink,
									'user'      : member.user,
									'team'      : requested_team,
									'message'   : message,
								}
								text_content = render_to_string('email/teamlmessage.html', context)
								msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
								msg.content_subtype = "html"  # Main content is now text/html
								msg.send()
								countemail += 1
							if request.POST['typemessage'] == "sms" or request.POST['typemessage'] == "both":
								## CREATE THE MESSAGE
								startmsg = 'Hello '+member.user.first_name+'\n\nThere is a new message from your teamleader in '+requested_team.name+'\n\n'
								messagecount = len(message)
								if messagecount >= 255:
									msglink = 'https://victory.genki.dk/message/?u='+str(member.user.id)+'&t='+str(emailsmsdata.token)
									middlemsg = 'To view it check your mail or click this link to read it directly\n'+msglink+'\n\n'
								else:
									middlemsg = message+'\n\n'
								endmsg = 'Best,\n'+requested_team.name
								## SEND IT
								gwapi = OAuth1Session('OCBzbvY1b1FCQpTzEa4_131V', client_secret='g^oqsxSClJ(A@-Yttu-D6.C5lB6YdeBVz&LJ6E3W')
								req = {
									'sender': 'Genki',
									'message': startmsg+middlemsg+endmsg,
									'recipients': [{'msisdn': member.user.extendeduser.phone_number[1:]}],
								}
								res = gwapi.post('https://gatewayapi.com/rest/mtsms', json=req)
								res.raise_for_status()
								countsms += 1
						messages.success(request, "Message send out to ALL! on "+requested_team.name+" Emails: "+str(countemail)+" SMS: "+str(countsms))
						return redirect('teamsettings_message', team_pk)
					else:
						token = str(uuid4().hex)
						emailsmsdata = EmailAndSmsMessages()
						emailsmsdata.token = token
						emailsmsdata.msgtype = typemessage
						emailsmsdata.team = requested_team
						emailsmsdata.subject = subject
						emailsmsdata.message = message
						emailsmsdata.save()
						for person in people:
							member = get_object_or_404(TeamMembership, pk=person)
							emailsmsdata.members.add(member)
							if request.POST['typemessage'] == "email" or request.POST['typemessage'] == "both":
								from_email, to = 'info@victory.genki.dk', member.user.email
								messagelink = '?u='+str(member.user.id)+'&t='+str(emailsmsdata.token)
								context = {
									'weblink'	: messagelink,
									'user'      : member.user,
									'team'      : requested_team,
									'message'   : message,
								}
								text_content = render_to_string('email/teamlmessage.html', context)
								msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
								msg.content_subtype = "html"  # Main content is now text/html
								msg.send()
								countemail += 1
							if request.POST['typemessage'] == "sms" or request.POST['typemessage'] == "both":
    							## CREATE THE MESSAGE
								startmsg = 'Hello '+member.user.first_name+'\n\nThere is a new message from your teamleader in '+requested_team.name+'\n\n'
								messagecount = len(message)
								if messagecount >= 255:
									msglink = 'https://victory.genki.dk/message/?u='+str(member.user.id)+'&t='+str(emailsmsdata.token)
									middlemsg = 'To view it check your mail or click this link to read it directly\n'+msglink+'\n\n'
								else:
									middlemsg = message+'\n\n'
								endmsg = 'Best,\n'+requested_team.name
								## SEND IT
								gwapi = OAuth1Session('OCBzbvY1b1FCQpTzEa4_131V', client_secret='g^oqsxSClJ(A@-Yttu-D6.C5lB6YdeBVz&LJ6E3W')
								req = {
									'sender': 'Genki',
									'message': startmsg+middlemsg+endmsg,
									'recipients': [{'msisdn': member.user.extendeduser.phone_number[1:]}],
								}
								res = gwapi.post('https://gatewayapi.com/rest/mtsms', json=req)
								res.raise_for_status()
								countsms += 1
						messages.success(request, "Message send specific people in "+requested_team.name+" Emails: "+str(countemail)+" SMS: "+str(countsms))
						return redirect('teamsettings_message', team_pk)
	## THIS IS THE GET METHOD
	for member in memberships:
		if member.user.pk == request.user.pk and member.leader:
			feedback = FeedbackSupportForm()
			context = {
				'memberships':	memberships,
				'requested_team': requested_team,
				'feedback': feedback,
				'logged_in_user': logged_in_user,
			}
			return render(request, 'team/message.html', context)
	return redirect('team', team_pk)

@login_required
def teamsettings_logo(request, team_pk):
	requested_team = get_object_or_404(Team, pk=team_pk)
	if request.method == 'POST':
		for member in requested_team.teammembership_set.all().order_by('-leader'):
			if member.user.pk == request.user.pk and member.leader:
				form = UpdateTeamlogo(request.POST, request.FILES, instance=requested_team)
				if form.is_valid():
					form.save()
					messages.success(request, "You avatar have been uploaded!")
					return redirect('teamsettings_general', team_pk=team_pk)
	return redirect('team', team_pk)

@login_required
def teamsettings_background(request, team_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_team = get_object_or_404(Team, pk=team_pk)
	if request.method == 'POST':
		for member in requested_team.teammembership_set.all().order_by('-leader'):
			if member.user.pk == request.user.pk and member.leader:
				form = UpdateTeambackground(request.POST, request.FILES, instance=requested_team)
				if form.is_valid():
					form.save()
					messages.success(request, "You avatar have been uploaded!")
					return redirect('teamsettings_general', team_pk=team_pk)
	return redirect('team', team_pk)

@login_required
def teamsettings_description(request, team_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_team = get_object_or_404(Team, pk=team_pk)
	if request.method == 'POST':
		for member in requested_team.teammembership_set.all().order_by('-leader'):
			if member.user.pk == request.user.pk and member.leader:
				form = TeamSettings_DescriptionForm(request.POST, instance=requested_team)
				if form.is_valid():
					form.save()
					messages.success(request, "The team has been updated!")
					return redirect('teamsettings_description', team_pk=team_pk)
	for member in requested_team.teammembership_set.all().order_by('-leader'):
		if member.user.pk == request.user.pk and member.leader:
			feedback = FeedbackSupportForm()
			form = TeamSettings_DescriptionForm(request.POST, instance=requested_team)
			context = {
				'requested_team': requested_team,
				'feedback': feedback,
				'form' : form,
				'logged_in_user': logged_in_user,
			}
			return render(request, 'team/description.html', context)
			break
	return redirect('team', team_pk)

@login_required
def teamsettings_members(request, team_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_team = get_object_or_404(Team, pk=team_pk)
	for member in requested_team.teammembership_set.all().order_by('-leader'):
		if member.user.pk == request.user.pk and member.leader:
			feedback = FeedbackSupportForm()
			context = {
				'requested_team': requested_team,
				'feedback': feedback,
				'logged_in_user': logged_in_user,
			}
			return render(request, 'team/members.html', context)
			break
	return redirect('team', team_pk)

@login_required
def teamsettings_members_add(request, team_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_team = get_object_or_404(Team, pk=team_pk)
	for member in requested_team.teammembership_set.all().order_by('-leader'):
		if member.user.pk == request.user.pk and member.leader:
			if request.method == 'POST':
				teammemberships = TeamMembership.objects.all().filter(user=request.POST['user'])
				for memberships in teammemberships:
					if memberships.accepted:
						messages.success(request, "Error - User is already on a team.")
						return redirect('teamsettings_members', team_pk=team_pk)
				formaddmember = TeamSettings_AddForm(request.POST)
				if formaddmember.is_valid():
					formaddmember.save()
					messages.success(request, "User had been added to your team!")
					return redirect('teamsettings_members', team_pk=team_pk)
			else:
				users = User.objects.all().order_by('username')
				feedback = FeedbackSupportForm()
				addmember = TeamSettings_AddForm()
				context = {
					'requested_team': requested_team,
					'users': users,
					'feedback': feedback,
					'addmember': addmember,
					'logged_in_user': logged_in_user,
				}
				return render(request, 'team/add_member.html', context)
				break
	return redirect('team', team_pk)

@login_required
def teamsettings_members_delete(request, team_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_team = get_object_or_404(Team, pk=team_pk)
	for member in requested_team.teammembership_set.all().order_by('-leader'):
		if member.user.pk == request.user.pk and member.leader:
			if request.method == 'POST':
				userpk = request.POST['user']
				membershippk = request.POST['membership']
				TeamMembership.objects.filter(user=userpk).filter(id=membershippk).delete()
				messages.success(request, "User successful removed from the team.")
				return redirect('teamsettings_members', team_pk=team_pk)

@login_required
def teamsettings_applications(request, team_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_team = get_object_or_404(Team, pk=team_pk)
	for member in requested_team.teammembership_set.all().order_by('-leader'):
		if member.user.pk == request.user.pk and member.leader:
			feedback = FeedbackSupportForm()
			formaccept = TeamSettings_acceptForm()
			formneedinfoandrefuse = TeamSettings_needinfo_andrefuseForm()
			teamapplications = TeamApplication.objects.all().filter(to_team=requested_team.pk).order_by('send')
			context = {
				'requested_team': requested_team,
				'feedback': feedback,
				'formaccept': formaccept,
				'formneedinfoandrefuse': formneedinfoandrefuse,
				'logged_in_user': logged_in_user,
				'applications': teamapplications,
			}
			return render(request, 'team/applications.html', context)
	return redirect('team', team_pk)

@login_required
def teamsettings_accept_applications(request, team_pk):
	if request.method == 'POST': #check if post
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		requested_team = get_object_or_404(Team, pk=team_pk)
		for member in requested_team.teammembership_set.all().order_by('-leader'): #Foreach TeamMembership in this team check if current user is leader for the team.
			if member.user.pk == request.user.pk and member.leader:
				formaccept = TeamSettings_acceptForm(request.POST)
				accepteduserid = formaccept.data['user']
				teamapplications = TeamApplication.objects.all().filter(from_user=accepteduserid)
				for application in teamapplications:
					if application.accepted:
						messages.success(request, "Error - User is already on a team.")
						return redirect('teamsettings_applications', team_pk=team_pk)
				if teamapplications.count() > 1: #if user has more than one application.
					if formaccept.is_valid(): #user only has this application and form is valid then add him to the team.
						teamapplications = TeamApplication.objects.all().filter(from_user=accepteduserid).filter(to_team=requested_team)
						teamapplications.update(need_user_accept=True)
						getuser = get_object_or_404(User, pk=accepteduserid)
						subject = "Genki: You been accepted to join the team: "+requested_team.name
						from_email = 'info@victory.genki.dk'
						message = "You been accepted to join the team "+requested_team.name+" If this is the only team you send an application to then you'd be automaticly added. Else you will need to login to accept it yourself. Best, The team behind Victory"
						try:
							send_mail(subject, message, from_email, [getuser.email,], fail_silently=False,)
						except BadHeaderError:
							return HttpResponse('Invalid header found.')

						messages.success(request, "The accepted user has applied to multiple teams, he/she must validate that they want to join this team.")
						return redirect('teamsettings_applications', team_pk=team_pk)
				else:
					if formaccept.is_valid(): #user only has this application and form is valid then add him to the team.
						teamapplications = TeamApplication.objects.all().filter(from_user=accepteduserid)
						teamapplications.update(accepted=True)
						new_team_membership = formaccept.save(commit=False)
						new_team_membership.team = requested_team
						new_team_membership.save()
						newmember = get_object_or_404(User, pk=accepteduserid)
						#Send email SMS
						subject = "Genki: You been accepted to join the team: "+requested_team.name
						from_email = 'info@victory.genki.dk'
						message = "You been accepted to join the team "+requested_team.name+" If this is the only team you send an application to then you'd be automaticly added. Best, The team behind Victory"
						try:
							send_mail(subject, message, from_email, [newmember.email,], fail_silently=False,)
						except BadHeaderError:
							return HttpResponse('Invalid header found.')

						messages.success(request, "User has now been added to your team! And an email has been send to the user.")
						return redirect('teamsettings_members', team_pk=team_pk)

@login_required
def teamsettings_needinfo_applications(request, team_pk):
	if request.method == 'POST': #check if post
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		requested_team = get_object_or_404(Team, pk=team_pk)
		for member in requested_team.teammembership_set.all().order_by('-leader'): #Foreach TeamMembership in this team check if current user is leader for the team.
			if member.user.pk == request.user.pk and member.leader:
				formneedinfo = TeamSettings_needinfo_andrefuseForm(request.POST)
				if formneedinfo.is_valid():
					accepteduserid = formneedinfo.data['user']
					teamapplications = TeamApplication.objects.all().filter(from_user=accepteduserid).filter(to_team=requested_team)
					teamapplications.update(need_info=True)
					if formneedinfo.cleaned_data.get('comment'):
						comment = formneedinfo.cleaned_data.get('comment')
						teamapplications.update(need_info_comment=comment)
					else:
						comment = False
					newmember = get_object_or_404(User, pk=accepteduserid)
					#Send email SMS
					subject = "Genki: We need more info to the team: "+requested_team.name
					from_email = 'info@victory.genki.dk'
					message = "You been asked to send more info to the team "+requested_team.name+" The way you send more info is that you delete the old application you have and send a new one. Also the Team leader may have left a comment, log into your account and go check it out.  Best, The team behind Victory"
					try:
						send_mail(subject, message, from_email, [newmember.email,], fail_silently=False,)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					messages.success(request, "We have notified the user (By email) that you want more info.")
					return redirect('teamsettings_applications', team_pk=team_pk)

@login_required
def teamsettings_refuse_applications(request, team_pk):
	if request.method == 'POST': #check if post
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		requested_team = get_object_or_404(Team, pk=team_pk)
		for member in requested_team.teammembership_set.all().order_by('-leader'): #Foreach TeamMembership in this team check if current user is leader for the team.
			if member.user.pk == request.user.pk and member.leader:
				formrefuse = TeamSettings_needinfo_andrefuseForm(request.POST)
				if formrefuse.is_valid():
					accepteduserid = formrefuse.data['user']
					teamapplications = TeamApplication.objects.all().filter(from_user=accepteduserid).filter(to_team=requested_team)
					teamapplications.update(refused=True)
					if formrefuse.cleaned_data.get('comment'):
						comment = formrefuse.cleaned_data.get('comment')
						teamapplications.update(refused_comment=comment)
					else:
						comment = False
					newmember = get_object_or_404(User, pk=accepteduserid)
					#Send email SMS
					subject = "Genki: Refused to join the team: "+requested_team.name
					from_email = 'info@victory.genki.dk'
					message = "You been Refused to join the team "+requested_team.name+" There can be many reasons why but you can allways send a new one. Also the Team leader may have left a comment, log into your account and go check it out. Best, The team behind Victory"
					try:
						send_mail(subject, message, from_email, [newmember.email,], fail_silently=False,)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					messages.success(request, "We have notified the user (By email) that the application is refused")
					return redirect('teamsettings_applications', team_pk=team_pk)

@login_required
def apply(request):
	if request.method == 'POST':
			form = SendApplication(request.POST)
			if form.is_valid():
				form.save()
				messages.success(request, "Your application has now been send! you will get an email once a teamleader has reviewed your application")
				return redirect('index')
	else:
		teamapplication = TeamApplication.objects.all().filter(from_user=request.user.pk)
		teams = Team.objects.all().order_by('name')
		form = SendApplication()
		feedback = FeedbackSupportForm()
		context = {
			'teamapplication': teamapplication,
			'teams': teams,
			'form' : form,
			'feedback': feedback,
		}

		if request.user.is_authenticated():
			logged_in_user = get_object_or_404(User, pk=request.user.pk)
			context['logged_in_user'] = logged_in_user
			if TeamMembership.objects.all().filter(user=request.user.pk).count() > 1:
				context['onateam'] = True

		return render(request, 'apply.html', context)


@login_required
def applysent(request):
	teamapplication = TeamApplication.objects.all().filter(from_user=request.user.pk).order_by('send')
	teams = Team.objects.all().order_by('name')
	feedback = FeedbackSupportForm()
	context = {
		'teams': teams,
		'teamapplication' : teamapplication,
		'feedback': feedback,
	}

	if request.user.is_authenticated():
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		context['logged_in_user'] = logged_in_user
		if TeamMembership.objects.all().filter(user=request.user.pk).count() > 0:
			context['onateam'] = True

	return render(request, 'applysend.html', context)

@login_required
def useraccept(request):
	if request.method == 'POST':
		teamapppk = request.POST['apply_pk']
		teampk = request.POST['team_pk']
		requested_team = get_object_or_404(Team, pk=teampk)
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		teamapplications = TeamApplication.objects.all().filter(id=teamapppk)
		teamapplications.update(accepted=True)
		new_team_membership = TeamMembership()
		new_team_membership.user = logged_in_user
		new_team_membership.team = requested_team
		new_team_membership.save()
		messages.success(request, "Grats you have now joined the team - "+requested_team.name)
		return redirect('applysent')
	else:
		messages.error(request, "Couldn get the Application you wanted to accept.")
		return redirect('applysent')

@login_required
def applydelete(request):
	if request.method == 'POST':
		teamapppk = request.POST['apply_pk']
		TeamApplication.objects.filter(id=teamapppk).delete()
		messages.success(request, "Application successful got deleted!")
		return redirect('applysent')
	else:
		messages.error(request, "Couldn get the Application you wanted to delete.")
		return redirect('applysent')
