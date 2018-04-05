from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TeamApplication, Team, TeamMembership, TShirt, DriversLicenceCategories, Language
from django.forms import ModelChoiceField, ModelMultipleChoiceField

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

class TshirtChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.description

class DriversLicenceCategoriesMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.category

class LanguageMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class UpdateProfileForm(forms.ModelForm):
	birthdate = forms.DateField(input_formats=['%d-%m-%Y'],required=False)
	phone_number = forms.CharField(max_length=16, required=True)
	phone_number_show = forms.BooleanField(required=False)
	emergency_number = forms.CharField(max_length=16, required=False)
	postal_code = forms.CharField(max_length=10, required=True)
	languages = LanguageMultipleChoiceField(queryset=Language.objects.all(),required=False)
	drivers_licence = DriversLicenceCategoriesMultipleChoiceField(queryset=DriversLicenceCategories.objects.all(),required=False)
	tshirt = TshirtChoiceField(queryset=TShirt.objects.all(),required=False)
	special_considerations = forms.CharField(required=False)
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'birthdate', 'phone_number', 'phone_number_show', 'emergency_number', 'postal_code', 'languages', 'drivers_licence', 'tshirt', 'special_considerations',)

class UpdateSociallinksForm(forms.ModelForm):
	facebook_link = forms.URLField(max_length=200, required=False)
	twitter_link = forms.URLField(max_length=200, required=False)
	soundcloud_link = forms.URLField(max_length=200, required=False)
	youtube_link = forms.URLField(max_length=200, required=False)
	class Meta:
		model = User
		fields = ('facebook_link','twitter_link','soundcloud_link','youtube_link', )

class UpdateProfileAvatar(forms.ModelForm):
	avatar = forms.ImageField()
	class Meta:
		model = User
		fields = ('avatar',)

class UpdateProfileBackground(forms.ModelForm):
	background = forms.ImageField()
	class Meta:
		model = User
		fields = ('background',)

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

class UpdateTeamlogo(forms.ModelForm):
	logo = forms.ImageField()
	class Meta:
		model = Team
		fields = ('logo',)

class UpdateTeambackground(forms.ModelForm):
	background = forms.ImageField()
	class Meta:
		model = Team
		fields = ('background',)

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
	comment = forms.CharField(widget=forms.Textarea, required=False)
	class Meta:
		fields = ('user', 'comment',)

class TeamSettings_AddForm(forms.ModelForm):
	class Meta:
		model = TeamMembership
		fields = ('user','team', 'leader')
