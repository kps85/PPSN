from django import forms

from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import User, UserProfile
from django.contrib.auth.forms import AuthenticationForm


class RegistrationForm(forms.Form):
	first_name = forms.CharField(max_length=100, min_length=1)
	username = forms.CharField(max_length=100, min_length=1)
	password = forms.CharField(max_length=100)
	email = forms.EmailField(max_length=100)


class LoginForm(forms.Form):
	username = forms.CharField(max_length=100, min_length=1)
	password = forms.CharField(max_length=100)


class UserForm(ModelForm):
	username = forms.CharField()
	email = forms.EmailField()
	first_name = forms.CharField()
	last_name = forms.CharField()

	class Meta:
		model = User
		fields = ['username', 'email', 'first_name', 'last_name']


	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance')
		super(UserForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['readonly'] = True
		for field in self.fields:
			self.fields[field].widget.attrs['class'] = 'form-control'
			if field != 'ack_password' and field != 'password':
				self.fields[field].widget.attrs['value'] = getattr(instance, field)


# Change your password
class SetPasswordForm(forms.Form):
	error_messages = {'password_mismatch': ("The two password fields didn't match."),}
	new_password1 = forms.CharField(label=("New password"),
                                    widget=forms.PasswordInput)
	new_password2 = forms.CharField(label=("New password confirmation"),
                                    widget=forms.PasswordInput)
	def __init__(self, user, *args, **kwargs):
		self.user = user
		super(SetPasswordForm, self).__init__(*args, **kwargs)

	def clean_new_password2(self):
		password1 = self.cleaned_data.get('new_password1')
		password2 = self.cleaned_data.get('new_password2')
		if password1 and password2:
			if password1 != password2:
				raise forms.ValidationError(
					self.error_messages['password_mismatch'],
					code='password_mismatch',
				)
		return password2

	def save(self, commit=True):
		self.user.set_password(self.cleaned_data['new_password1'])
		if commit:
			self.user.save()
		return self.user

class UserDataForm(ModelForm):
	class Meta:
		model = UserProfile
		fields = ['picture', 'academicDiscipline', 'studentNumber', 'location']

	# validation: check after sumit before save
	def clean_picture(self):
		# this is the current picture, nothing will happen if checkbox not clicked

		picture = self.cleaned_data.get('picture')
		print(picture)
		# checkbox (False if clicked) -> return default picture
		if picture == False:
			return 'default.gif'
		return picture

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance')
		super(UserDataForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			if field != 'picture':
				self.fields[field].widget.attrs['class'] = 'form-control'
			self.fields[field].widget.attrs['value'] = getattr(instance, field)