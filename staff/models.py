from django.db import models

from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

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

class TShirt(models.Model):
	description = models.CharField(max_length=32)

class Sock(models.Model):
	description = models.CharField(max_length=32)

class Review(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	overall_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
	on_time = models.NullBooleanField()
	comment = models.TextField(blank=True)

	def __str__(self):
		return str(self.overall_rating) + '/5, ' + self.user.extendeduser.nickname + '(' + self.user.username + ', ' + self.user.get_full_name() + ')'

class ExtendedUser(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	nickname = models.CharField(max_length=20)
	birthdate = models.DateField(null=True)
	phone_number_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+4570131415'. Up to 15 digits allowed.")
	phone_number = models.CharField(max_length=16, validators=[phone_number_regex], blank=True)
	emergency_number = models.CharField(max_length=16, validators=[phone_number_regex], blank=True)
	drivers_licence = models.ManyToManyField(DriversLicenceCategories, blank=True)
	avatar = models.ImageField(upload_to='users/avatars')
	background = models.ImageField(upload_to='users/backgrounds')
	team = models.ForeignKey(Team, null=True, blank=True) # Skal der være on_delete her?
	languages = models.ManyToManyField(Language)
	tshirt = models.ForeignKey(TShirt, null=True, blank=True)
	sock = models.ForeignKey(Sock, null=True, blank=True)
	facebook_link = models.URLField(max_length=200, blank=True, null=True)
	twitter_link = models.URLField(max_length=200, blank=True, null=True)
	soundcloud_link = models.URLField(max_length=200, blank=True, null=True)
	youtube_link = models.URLField(max_length=200, blank=True, null=True)
	child_record = models.DateField(null=True, blank=True)
	special_considerations = models.TextField(blank=True)

class Article(models.Model):
	author = models.ForeignKey(User)
	title = models.CharField(max_length=64)
	created = models.DateTimeField(null=True)
	body = models.TextField()

	def __str__(self):
		return self.title

class Alert(models.Model):
	title = models.CharField(max_length=32)
	body = models.TextField(blank=True)
	start = models.DateTimeField()
	end = models.DateTimeField()

class Unauthenticated_session(models.Model):
	user = models.ForeignKey(User)
	token = models.CharField(max_length=36)
	otp = models.PositiveSmallIntegerField()
	created = models.DateTimeField(auto_now_add=True)
	guesses_left = models.PositiveSmallIntegerField(default=3)
	successful = models.BooleanField(default=False)
