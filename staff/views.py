from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate as auth_authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Article, UnauthenticatedSession, Team, DriversLicenceCategories
from .forms import SignUpForm
from uuid import uuid4
from random import randint
import requests
import os
from requests_oauthlib import OAuth1Session


# Create your views here.

def index(request):
	if request.user.is_authenticated():
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		articles = Article.objects.all()

		context = {
			'logged_in_user': logged_in_user,
			'articles': articles,
		}

		return render(request, 'dashboard.html', context)
	else:
		return render(request, 'welcome.html')

def teams(request):
	teams = Team.objects.all()

	context = {
		'teams': teams,
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

				gwapi = OAuth1Session(os.environ['VICTORY_GATEWAYAPI_KEY'], client_secret=os.environ['VICTORY_GATEWAYAPI_SECRET'])

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

				return render(request, "2ndfactor.html", {'token': token})
			else:
				return render(request, "login.html", {'invalid': True })
		else:
			return render(request, "login.html")
	else:
		return render(request, 'login.html')

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
	return render(request, 'register.html', {'form': form})

def registerimage(request):
	return render(request, 'registerimage.html', {})

@login_required
def users(request):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	users = User.objects.all()
	context = {
		'logged_in_user': logged_in_user,
		'users': users,
	}

	return render(request, 'users.html', context)

@login_required
def user(request, user_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_user = get_object_or_404(User, pk=user_pk)

	context = {
		'logged_in_user': logged_in_user,
		'requested_user': requested_user,
		'editable': True # Has to do actual permission logic.
	}

	return render(request, 'user/profile.html', context)

@login_required
def usersettings(request, user_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_user = get_object_or_404(User, pk=user_pk)
	driverslicence = DriversLicenceCategories.objects.all()

	context = {
		'logged_in_user': logged_in_user,
		'requested_user': requested_user,
		'driverslicence': driverslicence,
	}

	return render(request, 'user/settings.html', context)

def team(request, team_pk):
	requested_team = get_object_or_404(Team, pk=team_pk)

	context = {
		'requested_team': requested_team,
	}

	if requested_team.multiple_teamleaders:
		context["multiple_teamleaders"] = True

	if request.user.is_authenticated():
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		context['logged_in_user'] = logged_in_user

	return render(request, 'team/team.html', context)

def teamsettings(request, team_pk):
	requested_team = get_object_or_404(Team, pk=team_pk)

	if request.user.is_authenticated():
		logged_in_user = get_object_or_404(User, pk=request.user.pk)

	context = {
		'requested_team': requested_team,
		'logged_in_user': logged_in_user,
	}
	return render(request, 'team/settings.html', context)

@login_required
def apply(request):
	teams = Team.objects.all()

	context = {
		'teams': teams,
	}

	if request.user.is_authenticated():
		logged_in_user = get_object_or_404(User, pk=request.user.pk)
		context['logged_in_user'] = logged_in_user

	return render(request, 'apply.html', context)
