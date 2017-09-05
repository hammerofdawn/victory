from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.http import HttpResponse
from django.template import loader

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Article


def login(request):
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
