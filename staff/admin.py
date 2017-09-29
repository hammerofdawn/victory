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
	Review,
	Alert,
	UnauthenticatedSession,
	Group,
	GroupMembership,
	TeamMembership,
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

class GroupMembershipInline(admin.TabularInline):
	model = GroupMembership
	extra = 1

class GroupAdmin(admin.ModelAdmin):
	filter_horizontal = ['members']
	inlines = (GroupMembershipInline, )

class TeamAdmin(admin.ModelAdmin):
	filter_horizontal = ['members']
	inlines = (TeamMembershipInline, )

class UnauthenticatedSessionAdmin(admin.ModelAdmin):
	list_display = ('user', 'token', 'successful')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(DriversLicenceCategories)
admin.site.register(Language)
admin.site.register(Article)
admin.site.register(TShirt)
admin.site.register(Sock)
admin.site.register(Review)
admin.site.register(Alert)
admin.site.register(UnauthenticatedSession, UnauthenticatedSessionAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(TeamMembership)
