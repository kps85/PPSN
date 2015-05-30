from django import forms

from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import User, UserProfile


class RegistrationForm(forms.Form):
	first_name = forms.CharField(max_length=100, min_length=1)
	username = forms.CharField(max_length=100, min_length=1)
	password = forms.CharField(max_length=100)
	email = forms.EmailField(max_length=100)


class LoginForm(forms.Form):
	username = forms.CharField(max_length=100, min_length=1)
	password = forms.CharField(max_length=100)


class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ['username', 'password', 'email', 'first_name', 'last_name']

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance')
		super(UserForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['readonly'] = True
		self.fields['password'].widget = forms.PasswordInput()
		for field in self.fields:
			self.fields[field].widget.attrs['class'] = 'form-control'
			self.fields[field].widget.attrs['value'] = getattr(instance, field)


class UserDataForm(ModelForm):
	class Meta:
		model = UserProfile
		fields = ['picture', 'academicDiscipline', 'studentNumber', 'location']

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance')
		super(UserDataForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			if field != 'picture':
				self.fields[field].widget.attrs['class'] = 'form-control'
			self.fields[field].widget.attrs['value'] = getattr(instance, field)