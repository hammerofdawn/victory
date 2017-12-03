from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate as auth_authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from .models import Article, UnauthenticatedSession, Team, DriversLicenceCategories, TeamApplication, TeamMembership
from .forms import SignUpForm, UpdateProfileForm, SendApplication, FeedbackSupportForm
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

	if request.method == 'POST':
		token = request.POST.get('token', None)
		username = request.POST.get('username', None)
		password = request.POST.get('password', None)

		if token is not None:
			otpdigit1 = request.POST.get('otpdigit1', '')
			otpdigit2 = request.POST.get('otpdigit2', '')
			otpdigit3 = request.POST.get('otpdigit3', '')
			otpdigit4 = request.POST.get('otpdigit4', '')

			otp = otpdigit1 + otpdigit2 + otpdigit3 + otpdigit4

			if len(otp) == 4:
				ua = UnauthenticatedSession.objects.get(token=str(token))

				if ua.guesses_left > 0:
					if ua.successful == False:
						if otp == ua.otp:
							ua.successful = True
							ua.save()

							auth_login(request, ua.user)
							return redirect('index')
						else:
							ua.guesses_left -= 1
							ua.save()

							return render(request, "2ndfactor.html", {
								'error': "The entered code was incorrect.",
								'token': token
							})
					else:
						return render(request, "2ndfactor.html", {
							'error': "Token has already been used.",
						})
				else:
					return render(request, "2ndfactor.html", {
						'error': "Code has been entered incorrectly too many times.",
					})
			else:
				return render(request, "2ndfactor.html", {'error': True})

		elif username and password:
			user = auth_authenticate(request, username=username, password=password)

			if user is not None:
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
				return render(request, "login.html", {'invalid': True, 'feedback': feedback, })
		else:
			feedback = FeedbackSupportForm()
			return render(request, "login.html", {'feedback': feedback,})
	else:
		feedback = FeedbackSupportForm()
		return render(request, 'login.html', {'feedback': feedback,})

#def welcome(request):
#	return render(request, 'welcome.html', {})

def logout(request):
	auth_logout(request)
	return redirect('index')

def register(request):
	if request.method == 'POST':
			form = SignUpForm(request.POST)
			if form.is_valid():
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
	else:
		form = SignUpForm()
		feedback = FeedbackSupportForm()
	return render(request, 'register.html', {'form': form, 'feedback': feedback,})

def registerimage(request):
	feedback = FeedbackSupportForm()
	return render(request, 'registerimage.html', {'feedback': feedback,})

def contact(request):
	if request.method == 'POST':
		form = FeedbackSupportForm(request.POST)
		if form.is_valid():
			user_mail = form.cleaned_data['email']
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			subject = "Message from contact form. Victory"
			from_email = 'info@victory.genki.dk'
			message = "New mail from: "+first_name+" "+last_name+" "+user_mail+" : "+form.cleaned_data['message']
			try:
				send_mail(subject, message, from_email, ['melonendk@gmail.com', 'deni@radera.net'], fail_silently=False,)
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

	context = {
		'logged_in_user': logged_in_user,
		'requested_user': requested_user,
		'editable': True, # Has to do actual permission logic.
		'feedback': feedback,
	}

	return render(request, 'user/profile.html', context)

@login_required
def usersettings(request, user_pk):
	if request.method == 'POST':
		form = UpdateProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			user = form.save()
			user.refresh_from_db()  # load the profile instance created by the signal
			user.extendeduser.postal_code = form.cleaned_data.get('postal_code')
			user.extendeduser.phone_number = form.cleaned_data.get('phone_number')
			user.extendeduser.nickname = form.cleaned_data.get('username')
			user.extendeduser.phone_number_show = form.cleaned_data.get('phone_number_show')
			user.save()
			messages.success(request, "Your profile has been updated!")
			return redirect('usersettings', user_pk=request.user.pk)

	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_user = get_object_or_404(User, pk=user_pk)
	driverslicence = DriversLicenceCategories.objects.all()
	form = UpdateProfileForm(instance=request.user)
	feedback = FeedbackSupportForm()
	password = PasswordChangeForm(request.user)
	context = {
		'logged_in_user': logged_in_user,
		'requested_user': requested_user,
		'driverslicence': driverslicence,
		'form'			: form,
		'feedback'		: feedback,
		'password'		: password,
	}
	return render(request, 'user/settings.html', context)

def user_change_password(request, user_pk):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password was successfully updated!')
			return redirect('usersettings', user_pk=request.user.pk)
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		redirect('usersettings', user_pk=request.user.pk)

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

	return render(request, 'team/team.html', context)

@login_required
def teamsettings_general(request, team_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_team = get_object_or_404(Team, pk=team_pk)
	for member in requested_team.teammembership_set.all():
		if member.user.pk == request.user.pk:
			feedback = FeedbackSupportForm()
			context = {
				'requested_team': requested_team,
				'feedback': feedback,
				'logged_in_user': logged_in_user,
			}
			return render(request, 'team/settings.html', context)
			break
		else: return redirect('team', team_pk)


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

	return render(request, 'applysend.html', context)

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
