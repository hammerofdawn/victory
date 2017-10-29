from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
	postal_code = forms.CharField(max_length=10, required=True)
	phone_number = forms.CharField(max_length=16, required=True)

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'postal_code', 'phone_number', 'password1', 'password2', )

class UpdateProfileForm(forms.ModelForm):
	postal_code = forms.CharField(max_length=10, required=True)
	phone_number = forms.CharField(max_length=16, required=True)

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'postal_code', 'phone_number',)
