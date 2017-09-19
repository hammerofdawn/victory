from django.shortcuts import get_object_or_404, render, redirect

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate as auth_authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Article


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth_authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            return render(request, "login.html", {'invalid': True })
    else:
        return render(request, 'login.html')

'''
@login_required
def staff(request):
    logged_in_user = get_object_or_404(User, pk=request.user.pk)
    requested_user = get_object_or_404(User, pk=user_id)
    users = User.objects.all()

    context = {
        'logged_in_user': logged_in_user,
        'requested_user': requested_user,
        'users': users,
    }

    return render(request, 'dashboard.html', context)
'''

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
    context = {
        'logged_in_user': logged_in_user,
    }

    return render(request, 'teams.html', context)

@login_required
def team(request, team_pk):
    logged_in_user = get_object_or_404(User, pk=request.user.pk)
    context = {
        'logged_in_user': logged_in_user,
    }

    return render(request, 'team.html', context)
