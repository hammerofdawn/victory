from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from django import forms

# Register your models here.
from .models import (
	ExtendedUser,
	Team,
	DriversLicenceCategories,
	Language,
	Article,
	TShirt,
	Sock,
	Alert,
	UnauthenticatedSession,
	TeamMembership,
	TeamApplication,
	TeamGroup,
)

class UserInline(admin.StackedInline):
	model = ExtendedUser
	can_delete = False
	filter_horizontal = ['drivers_licence', 'languages']

class UserAdmin(BaseUserAdmin):
	inlines = (UserInline, )

class TeamMembershipInline(admin.TabularInline):
	model = TeamMembership
	extra = 1

class TeamAdmin(admin.ModelAdmin):
	filter_horizontal = ['members']
	inlines = (TeamMembershipInline, )
	list_display = ('name', 'people_needed', 'accepts_applications')
	ordering = ('name',)

class UnauthenticatedSessionAdmin(admin.ModelAdmin):
	list_display = ('user', 'token', 'successful')

class TeamApplicationAdmin(admin.ModelAdmin):
	list_display = ('from_user', 'accepted', 'need_info', 'refused')
	ordering = ('-from_user',)

class TeamMembershipAdmin(admin.ModelAdmin):
	list_display = ('team', 'user', 'leader')
	ordering = ('team',)

admin.site.register(TeamGroup)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(DriversLicenceCategories)
admin.site.register(Language)
admin.site.register(Article)
admin.site.register(TShirt)
admin.site.register(Sock)
admin.site.register(Alert)
admin.site.register(UnauthenticatedSession, UnauthenticatedSessionAdmin)
admin.site.register(TeamMembership, TeamMembershipAdmin)
admin.site.register(TeamApplication, TeamApplicationAdmin)
