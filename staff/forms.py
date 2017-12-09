from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import TeamApplication, Team, TeamMembership

class SignUpForm(UserCreationForm):
	postal_code = forms.CharField(max_length=10, required=True)
	phone_number = forms.CharField(max_length=16, required=True)

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'postal_code', 'phone_number', 'password1', 'password2', )

	def clean(self):
		cleaned_data = super(SignUpForm, self).clean()
		username = cleaned_data.get('username')
		if username and User.objects.filter(username__iexact=username).exists():
			self.add_error('username', 'A user with that username already exists.')
		return cleaned_data

class UpdateProfileForm(forms.ModelForm):
	postal_code = forms.CharField(max_length=10, required=True)
	phone_number = forms.CharField(max_length=16, required=True)
	phone_number_show = forms.BooleanField(required=False)
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'postal_code', 'phone_number', 'phone_number_show',)

class SendApplication(forms.ModelForm):
	class Meta:
		model = TeamApplication
		fields = ('from_user', 'to_team', 'application_text',)

class FeedbackSupportForm(forms.Form):
	first_name = forms.CharField(max_length=30, required=True)
	last_name = forms.CharField(max_length=30, required=True)
	email = forms.EmailField(required=True)
	message = forms.CharField(widget=forms.Textarea, required=True)

	class Meta:
		fields = ('username', 'first_name', 'last_name', 'email', 'message',)

class TeamSettings_GeneralForm(forms.ModelForm):
	class Meta:
		model = Team
		fields = ('name', 'accepts_applications',)

class TeamSettings_DescriptionForm(forms.ModelForm):
	class Meta:
		model = Team
		fields = ('description',)

class TeamSettings_acceptForm(forms.ModelForm):
	class Meta:
		model = TeamMembership
		fields = ('user',)

class TeamSettings_needinfo_andrefuseForm(forms.Form):
	user = forms.IntegerField()
	class Meta:
		fields = ('user',)
