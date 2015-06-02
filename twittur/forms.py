from django import forms

from django.core.exceptions import ValidationError, FieldError
from django.contrib.auth.hashers import make_password, is_password_usable
from django.contrib.auth.models import User
from django.forms import ModelForm

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
	ack_password = forms.CharField(max_length=128, widget = forms.PasswordInput, required=False)

	class Meta:
		model = User
		fields = ['username', 'password', 'ack_password', 'email', 'first_name', 'last_name']

	def clean(self):
		password = self.cleaned_data.get('password')
		ack_password = self.cleaned_data.get('ack_password')
		error_dict = {}
		if password != ack_password:
			error_dict['ack_password'] = 'Passwoerter stimmen nicht ueberein!'
		if ' ' in password:
			error_dict['password'] = 'Keine Leerzeichen im Passwort erlaubt!'
		if len(error_dict) > 0:
			raise ValidationError(error_dict, code='invalid')
		return self.cleaned_data

	def save(self, commit=True):
		instance = super(UserForm, self).save(commit=False)
		password = self.cleaned_data.get('password')
		if password:
			instance.set_password(password)
		if commit:
			instance.save()
		return instance

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance')
		super(UserForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['readonly'] = True
		self.fields['password'].widget = forms.PasswordInput()
		self.fields['password'].required = False
		for field in self.fields:
			self.fields[field].widget.attrs['class'] = 'form-control'
			if field != 'ack_password' and field != 'password':
				self.fields[field].widget.attrs['value'] = getattr(instance, field)


class UserDataForm(ModelForm):
	class Meta:
		model = UserProfile
		fields = ['picture', 'academicDiscipline', 'studentNumber', 'location']

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance')
		super(UserDataForm, self).__init__(*args, **kwargs)
		self.fields['location'].required = False
		for field in self.fields:
			if field != 'picture':
				self.fields[field].widget.attrs['class'] = 'form-control'
			self.fields[field].widget.attrs['value'] = getattr(instance, field)

	# validation: check after submit before save
	def clean_picture(self):
		# this is the current picture, nothing will happen if checkbox not clicked
		picture = self.cleaned_data.get('picture')
		# checkbox (False if clicked) -> return default picture
		if not picture:
			return 'picture/default.gif'
		return picture

	def save(self, commit=True):
		instance = super(UserDataForm, self).save(commit=False)
		oldPic = self.oldPicture
		print(oldPic)
		print(instance.picture)
		if oldPic != 'picture/default.gif' and oldPic != instance.picture and oldPic != '':
			oldPic.delete()
			print(commit)
		if commit:
			print('im commit')
			instance.save()
		return instance