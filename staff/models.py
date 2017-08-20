from django.db import models

from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=16)

    logo = models.ImageField(upload_to='teams/avatars')
    background = models.ImageField(upload_to='teams/backgrounds')

    requirements = models.TextField(blank=True)

    people_needed = models.PositiveSmallIntegerField()

    teamleaders = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class DriversLicenceCategories(models.Model): # No plural
    category = models.CharField(max_length=3)

    def __str__(self):
        return self.category


class Language(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name


class ExtendedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    nickname = models.CharField(max_length=20)

    phone_number_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+4570131415'. Up to 15 digits allowed.")
    phone_number = models.CharField(max_length=16, validators=[phone_number_regex], blank=True)

    drivers_licence = models.ManyToManyField(DriversLicenceCategories)

    avatar = models.ImageField(upload_to='users/avatars')
    background = models.ImageField(upload_to='users/backgrounds')

    team = models.ForeignKey(Team, null=True, blank=True) # Skal der være on_delete her?

    languages = models.ManyToManyField(Language)


class Article(models.Model):
    author = models.ForeignKey(User)
    title = models.CharField(max_length=64)
    body = models.TextField()

    def __str__(self):
        return self.title
