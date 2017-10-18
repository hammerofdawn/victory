from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate as auth_authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import Article, UnauthenticatedSession, Team, DriversLicenceCategories

from uuid import uuid4
from random import randint
import requests
from requests.auth import HTTPBasicAuth
import os


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
						if int(otp) == ua.otp:
							ua.successful = True
							ua.save()

							auth_login(request, ua.user)
							return redirect('index')
						else:
							ua.guesses_left -= 1
							ua.save()

							return render(request, "2ndfactor.html", {
								'invalid': True,
								'token': token
							})
					else:
						return render(request, "2ndfactor.html", {
							'error': "Token has already been used.",
						})
				else:
					return render(request, "2ndfactor.html", {
						'error': "Allowed number of attempts has been exceeded.",
					})
			else:
				return render(request, "2ndfactor.html", {'error': True})

		elif username and password:
			user = auth_authenticate(request, username=username, password=password)

			if user is not None:
				token = str(uuid4())
				otp = randint(1111, 9999)

				r = requests.post("https://api.tel.dk/api/1.0/message",
					auth=HTTPBasicAuth(
						os.environ['VICTORY_TELDK_EMAIL'],
						os.environ['VICTORY_TELDK_SECRET'],
					), headers={
						'content-type': 'application/x-www-form-urlencoded',
						'charset': 'utf-8',
					},
					data={
						'to': user.extendeduser.phone_number[1:],
						'text': 'Victory login code:\n' + str(otp)[0:1] + ' ' + str(otp)[1:2] + ' ' + str(otp)[2:3] + ' ' + str(otp)[3:4],
						'class': 0,
					}
				)

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
	return render(request, 'register.html', {})

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

@login_required
def userdescription(request, user_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_user = get_object_or_404(User, pk=user_pk)

	context = {
		'logged_in_user': logged_in_user,
		'requested_user': requested_user,
	}

	return render(request, 'user/description.html', context)

@login_required
def userimage(request, user_pk):
	logged_in_user = get_object_or_404(User, pk=request.user.pk)
	requested_user = get_object_or_404(User, pk=user_pk)

	context = {
		'logged_in_user': logged_in_user,
		'requested_user': requested_user,
	}

	return render(request, 'user/images.html', context)

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

	return render(request, 'team.html', context)

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
