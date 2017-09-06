from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.
from .models import ExtendedUser, Team, DriversLicenceCategories, Language, Article, TShirt, Sock, Review, Alert

class UserInline(admin.StackedInline):
    model = ExtendedUser
    can_delete = False
    filter_horizontal = ['drivers_licence', 'languages']

class UserAdmin(BaseUserAdmin):
    inlines = (UserInline, )

class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ['teamleaders']


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
