from django import forms

from django.core.exceptions import ValidationError, FieldError
from django.contrib.auth.hashers import make_password, is_password_usable
from django.contrib.auth.models import User
from django.forms import ModelForm, ChoiceField
from django.utils.safestring import mark_safe

from .models import User, UserProfile, Message, FAQ, Hashtag

AD_CHOICES = (
    (mark_safe('Fakult&auml;t I'), ()),
    (mark_safe('Fakult&auml;t II'), ()),
    (mark_safe('Fakult&auml;t III'), ()),
    (mark_safe('Fakult&auml;t IV'), (
        ('Automotive Systems', 'Automotive Systems'),
        ('Computational Neuroscience', 'Computational Neuroscience'),
        ('Elektrotechnik', 'Elektrotechnik'),
        ('ICT Innovation', 'ICT Innovation'),
        ('Informatik', 'Informatik'),
        ('Medieninformatik', 'Medieninformatik'),
        ('Technische Informatik', 'Technische Informatik'),
        ('Wirtschaftsinformatik', 'Wirtschaftsinformatik'),
    )),
    (mark_safe('Fakult&auml;t V'), ()),
    (mark_safe('Fakult&auml;t VI'), ()),
    (mark_safe('Fakult&auml;t VII'), ()),
)

class RegistrationUserForm(forms.Form):
    class Meta:
        model = User
        fields = ['firstname', 'username', 'email', 'password', 'ack_password', 'last_name']


class UserForm(ModelForm):
	ack_password = forms.CharField(max_length=128, widget=forms.PasswordInput, required=False)

	class Meta:
		model = User
		fields = ['username', 'password', 'ack_password', 'email', 'first_name', 'last_name']

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


class UserDataForm(ModelForm):
	class Meta:
		model = UserProfile
		fields = ['picture', 'academicDiscipline', 'studentNumber', 'location']

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance')
		super(UserDataForm, self).__init__(*args, **kwargs)
		self.fields['location'].required = False
		self.fields['studentNumber'].widget = forms.TextInput()
		self.fields['academicDiscipline'].widget = forms.Select(choices=AD_CHOICES)
		for field in self.fields:
			if field != 'picture':
				if field != 'studentNumber':
					self.fields[field].widget.attrs['class'] = 'form-control'
				else:
					self.fields[field].widget.attrs['class'] = 'form-control checkNumeric'
			if field != 'academicDiscipline':
				self.fields[field].widget.attrs['value'] = getattr(instance, field)
			else:
				self.fields['academicDiscipline'].initial = getattr(instance, field)

	# validation: check after submit before save
	def clean_picture(self):
		# this is the current picture, nothing will happen if checkbox not clicked
		picture = self.cleaned_data.get('picture')
		# checkbox (False if clicked) -> return default picture
		if picture == False:
			return 'picture/default.gif'
		return picture

	def save(self, commit=True):
		instance = super(UserDataForm, self).save(commit=False)
		if commit:
			instance.save()
		return instance


class MessageForm(ModelForm):
	class Meta:
		model = Message
		fields = ['user', 'text', 'date']

	def clean_text(self):
		text = self.cleaned_data.get('text')

		return text

	def __init__(self, *args, **kwargs):
		super(MessageForm, self).__init__(*args, **kwargs)
		self.fields['user'].widget = forms.HiddenInput()
		self.fields['date'].widget = forms.HiddenInput()
		self.fields['text'].widget = forms.Textarea(attrs=self.fields['text'].widget.attrs)
		self.fields['text'].widget.attrs['class'] = 'form-control'


class FAQForm(ModelForm):
	class Meta:
		model = FAQ
		fields = ['author', 'question', 'category', 'answer']

	def __init__(self, *args, **kwargs):
		super(FAQForm, self).__init__(*args, **kwargs)
		if 'instance' in kwargs:
			self.fields['author'].widget = forms.HiddenInput()
			user = kwargs.get('instance')
			self.fields['author'].initial = user.id
		self.fields['question'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Frage'})
		catChoices = (
			('Allgemeine Frage', 'Allgemeine Frage'),
			('Startseite', 'Startseite'),
			('Profilseite', 'Profilseite'),
			('Infoseite', 'Infoseite'),
			('Einstellungen', 'Einstellungen')
		)
		self.fields['category'] = forms.ChoiceField(choices=catChoices, widget=forms.Select)
		self.fields['answer'].widget = forms.Textarea(attrs={'rows': '5', 'placeholder': 'Antwort'})
		for field in self.fields:
			self.fields[field].widget.attrs['class'] = 'form-control'

	def save(self, commit=True):
		instance = super(FAQForm, self).save(commit=False)
		if commit:
			instance.save()
		return instance
