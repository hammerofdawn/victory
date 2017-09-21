from django.shortcuts import get_object_or_404, render, redirect

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate as auth_authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Article, Unauthenticated_session, Team

from uuid import uuid4
from random import randint

import nexmo


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
                print(token)
                ua = Unauthenticated_session.objects.get(token=str(token))

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
                return render(request, "2ndfactor.html", {'error': True})

        elif username and password:
            user = auth_authenticate(request, username=username, password=password)

            if user is not None:
                token = str(uuid4())
                otp = randint(1111, 9999)

                client = nexmo.Client()

                response = client.send_message({
                    'from': 'Genki',
                    'to': user.extendeduser.phone_number,
                    'text': 'Victory login code: ' + str(otp),
                    'message-class': 0,
                })
                response = response['messages'][0]

                if response['status'] == '0':
                    print('Sent message', response['message-id'])
                else:
                    print('Error:', response['error-text'])

                us = Unauthenticated_session()
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

def welcome(request):
    return render(request, 'welcome.html', {})

def logout(request):
    auth_logout(request)
    return redirect('login')

def register(request):
    return render(request, 'register.html', {})

@login_required
def index(request):
    logged_in_user = get_object_or_404(User, pk=request.user.pk)
    articles = Article.objects.all()

    context = {
        'logged_in_user': logged_in_user,
        'articles': articles,
    }

    return render(request, 'dashboard.html', context)


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
    }

    return render(request, 'user.html', context)


@login_required
def teams(request):
    logged_in_user = get_object_or_404(User, pk=request.user.pk)
    teams = Team.objects.all()
    context = {
        'logged_in_user': logged_in_user,
        'teams': teams,
    }

    return render(request, 'teams.html', context)

@login_required
def team(request, team_pk):
    logged_in_user = get_object_or_404(User, pk=request.user.pk)
    context = {
        'logged_in_user': logged_in_user,
    }

    return render(request, 'team.html', context)
