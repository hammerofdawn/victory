from django.db import models

from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Team(models.Model):
	name = models.CharField(max_length=50)
	logo = models.ImageField(upload_to='teams/avatars', default='static/img/userpreload.png')
	background = models.ImageField(upload_to='teams/backgrounds', default='static/img/userpreload.png')
	description = models.TextField(blank=True)
	people_needed = models.PositiveSmallIntegerField()
	members = models.ManyToManyField(User, through='TeamMembership')
	accepts_applications = models.BooleanField()

	@property
	def teamleaders_listable(self):
		leaders = self.members.filter(teammembership__leader=True)
		return ", ".join(l.extendeduser.nickname for l in leaders)

	@property
	def multiple_teamleaders(self):
		if len(self.members.filter(teammembership__leader=True)) > 1:
			return True
		else:
			return False

	def __str__(self):
		return self.name

class TeamMembership(models.Model):
	user = models.ForeignKey(User)
	team = models.ForeignKey(Team)
	leader = models.BooleanField(default=False)

class Group(models.Model):
	name = models.CharField(max_length=32)
	members = models.ManyToManyField(User, through='GroupMembership')
	team = models.ForeignKey(Team)

	def __str__(self):
		return self.name

class GroupMembership(models.Model):
	user = models.ForeignKey(User)
	group = models.ForeignKey(Group)
	leader = models.BooleanField()

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
	birthdate = models.DateField(null=True, blank=True)
	postal_code = models.CharField(max_length=10)
	phone_number_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+4570131415'. Up to 15 digits allowed.")
	phone_number = models.CharField(max_length=16, validators=[phone_number_regex], blank=True)
	phone_number_show = models.BooleanField(default=False)
	emergency_number = models.CharField(max_length=16, validators=[phone_number_regex], blank=True)
	drivers_licence = models.ManyToManyField(DriversLicenceCategories, blank=True)
	avatar = models.ImageField(upload_to='users/avatars', default='static/img/userpreload.png')
	background = models.ImageField(upload_to='users/backgrounds', default='static/img/userpreload.png')
	team = models.ForeignKey(Team, null=True, blank=True)
	languages = models.ManyToManyField(Language, blank=True)
	tshirt = models.ForeignKey(TShirt, null=True, blank=True)
	sock = models.ForeignKey(Sock, null=True, blank=True)
	facebook_link = models.URLField(max_length=200, blank=True, null=True)
	twitter_link = models.URLField(max_length=200, blank=True, null=True)
	soundcloud_link = models.URLField(max_length=200, blank=True, null=True)
	youtube_link = models.URLField(max_length=200, blank=True, null=True)
	child_record = models.DateField(null=True, blank=True)
	special_considerations = models.TextField(blank=True)

@receiver(post_save, sender=User)
def update_user_extendeduser(sender, instance, created, **kwargs):
    if created:
        ExtendedUser.objects.create(user=instance)
    instance.extendeduser.save()

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

class UnauthenticatedSession(models.Model):
	user = models.ForeignKey(User)
	token = models.CharField(max_length=36)
	otp = models.CharField(max_length=4)
	created = models.DateTimeField(auto_now_add=True)
	guesses_left = models.PositiveSmallIntegerField(default=3)
	successful = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username

class TeamApplication(models.Model):
	from_user = models.ForeignKey(User)
	send = models.DateTimeField(auto_now=False, auto_now_add=True)
	to_team = models.ManyToManyField(Team)
	application_text = models.TextField()
	accepted = models.BooleanField(default=False)
	need_info = models.BooleanField(default=False)
	refused = models.BooleanField(default=False)
