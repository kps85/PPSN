#-*- coding: utf-8 -*-
"""
-*- coding: utf-8 -*-
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
Forms
- UserForm              form to edit user account information
- UserDataForm          form to edit user profile information
- GroupProfileForm      form to create a new group
- GroupProfileEditForm  form to edit a group profile
- MessageForm           form to create a new message
- FAQForm               form to create a new FAQ entry
"""

import datetime
import re

from django import forms
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import User, UserProfile, Message, FAQ, GroupProfile


class UserForm(ModelForm):
    # initialize second pw input for confirmation
    ack_password = forms.CharField(max_length=128, widget=forms.PasswordInput, required=False)

    # referencing User model as basis for the form
    # initializing form input fields
    class Meta:
        model = User
        fields = ['username', 'password', 'ack_password', 'email', 'first_name', 'last_name']

    # method to initialize the form
    def __init__(self, *args, **kwargs):
        # get current user's information and set it
        instance = kwargs.get('instance')
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True  # set username input readonly
        self.fields['password'].widget = forms.PasswordInput()  # set pw input type to password
        self.fields['password'].required = False  # unset pw input as required

        # for each field set class to 'form-control' and
        # set initial value to user's information except pw and pw confirmation input
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            if field != 'ack_password' and field != 'password':
                self.fields[field].widget.attrs['value'] = getattr(instance, field)

    # method to compare password and password confirmation input values
    # if equal: return password
    # else: return error message
    def clean(self):
        password, ack_password = self.cleaned_data['password'], self.cleaned_data['ack_password']
        email = self.cleaned_data['email']
        error_dict = {}
        if password != ack_password:
            error_dict['ack_password'] = 'Passwoerter stimmen nicht ueberein!'
        if ' ' in password:
            error_dict['password'] = 'Keine Leerzeichen im Passwort erlaubt!'

        # EMail validation
        mail = email.split('@')
        if len(mail) == 1 or not (mail[1].endswith(".tu-berlin.de")
                                  or (email[(len(email) - 13):len(email)] == '@tu-berlin.de')):
            error_dict['email'] = "Keine g&uuml;ltige TU E-Mail Adresse!"

        if len(error_dict) > 0:
            raise ValidationError(error_dict, code='invalid')
        return self.cleaned_data

    # method to save user's updated information
    # 'set_password' is for encoding raw text password
    def save(self, commit=True):
        instance = super(UserForm, self).save(commit=False)
        password = self.cleaned_data['password']
        if password:
            instance.set_password(password)
        if commit:
            instance.save()
        return instance


class UserDataForm(ModelForm):
    # referencing UserProfile model as basis for the form
    # initializing form input fields
    class Meta:
        model = UserProfile
        fields = ['picture', 'academicDiscipline', 'studentNumber', 'location']

    # method to initialize the form
    def __init__(self, *args, **kwargs):
        # get current user's information and set it
        instance = kwargs.get('instance')
        super(UserDataForm, self).__init__(*args, **kwargs)
        # unset location as required
        self.fields['location'].required = False
        # picture only accepts images
        self.fields['picture'].widget.attrs['accept'] = 'image/*'
        # set studentNumber type to text
        self.fields['studentNumber'].widget = forms.TextInput(attrs={
            'pattern': '[0-9]{6}'
        })

        # for each field set class to 'form-control' except 'picture',
        # set class to 'checkNumeric' for studentNumber and
        # set initial value to user's personal information
        for field in self.fields:
            if field != 'picture':
                self.fields[field].widget.attrs['class'] = 'form-control'
            if field != 'academicDiscipline':
                self.fields[field].widget.attrs['value'] = getattr(instance, field)
            else:
                self.fields['academicDiscipline'].initial = getattr(instance, field)

    def clean(self):
        student_number = self.cleaned_data["studentNumber"]
        error_dict = {}
        if re.match("^[0-9]*$", student_number) is None:
            error_dict['studentNumber'] = "Die Matrikel-Nummer darf nur aus sechs Ziffern bestehen!"
        if len(error_dict) > 0:
            raise ValidationError(error_dict, code='invalid')
        return self.cleaned_data

    # validation: check after submit before save
    def clean_picture(self):
        # this is the current picture, nothing will happen if checkbox not clicked
        picture = self.cleaned_data['picture']
        # checkbox (False if clicked) -> return default picture
        if not picture:
            return 'picture/default.gif'
        return picture


class GroupProfileForm(ModelForm):
    ack_password = forms.CharField(max_length=128, widget=forms.PasswordInput, required=False)

    class Meta:
        model = GroupProfile
        fields = ['name', 'short', 'desc', 'password', 'picture']
        widgets = {
            'desc': forms.Textarea(attrs={'rows': 4, 'style': 'resize: none;'}),
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super(GroupProfileForm, self).__init__(*args, **kwargs)
        self.fields['picture'].widget.attrs['accept'] = 'image/*'
        for field in self.fields:
            if field != 'picture':
                self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        error_dict = {}
        name, short = self.cleaned_data['name'], self.cleaned_data['short']
        password, ack_password = self.cleaned_data['password'], self.cleaned_data['ack_password']

        group_list = GroupProfile.objects.all()
        for group in group_list:
            if name.lower() == group.name.lower():
                error_dict['name'] = "Sorry, Gruppenname ist bereits vergeben."
            if short.lower() == group.short.lower():
                error_dict['short'] = "Sorry, Gruppenabkürzung ist bereits vergeben."
        if 'name' or 'short' not in error_dict:
            if re.match("^[a-zA-Z0-9-_.]*$", short) is None:
                error_dict['short'] = "Nur 'A-Z, a-z, 0-9, -, _' und '.' in der Gruppenabkürzung erlaubt!"
        if password != ack_password:
            error_dict['ack_password'] = 'Passwörter stimmen nicht überein!'
        if ' ' in password:
            error_dict['password'] = 'Keine Leerzeichen im Passwort erlaubt!'
        if len(error_dict) > 0:
            raise ValidationError(error_dict, code='invalid')
        return self.cleaned_data


class GroupProfileEditForm(ModelForm):
    ack_password = forms.CharField(max_length=128, required=False)

    class Meta:
        model = GroupProfile
        fields = ['name', 'short', 'desc', 'password', 'picture']
        widgets = {
            'password': forms.PasswordInput,
            'desc': forms.Textarea(attrs={'rows': 4, 'style': 'resize: none;'}),
        }

    def __init__(self, *args, **kwargs):
        super(GroupProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['ack_password'].widget = forms.PasswordInput(attrs=self.fields['ack_password'].widget.attrs)
        self.fields['short'].widget.attrs['readonly'] = True  # set username input readonly
        self.fields['picture'].widget.attrs['accept'] = 'image/*'
        for field in self.fields:
            if field != 'picture':
                self.fields[field].widget.attrs['class'] = 'form-control'

    # method to compare password and password confirmation input values
    # if equal: return password
    # else: return error message
    def clean(self):
        name, short = self.cleaned_data['name'], self.cleaned_data['short']
        password, ack_password = self.cleaned_data['password'], self.cleaned_data['ack_password']
        group, group_list = GroupProfile.objects.get(short__exact=short), GroupProfile.objects.all()
        error_dict = {}
        for item in group_list:
            if item.name == name and item != group:
                error_dict['name'] = 'Eine Gruppe mit diesem Namen existiert bereits!'
            if item.short == short and item != group:
                error_dict['short'] = 'Eine Gruppe mit dieser Abk&uuml;rzung existiert bereits!'
        if password != '':
            if password != ack_password:
                error_dict['ack_password'] = 'Passw&ouml;rter stimmen nicht &uuml;berein!'
            elif ' ' in password:
                error_dict['password'] = 'Keine Leerzeichen im Passwort erlaubt!'
            else:
                self.cleaned_data['password'] = make_password(password)
        elif not check_password(password, group.password):
            self.cleaned_data['password'] = group.password

        if len(error_dict) > 0:
            raise ValidationError(error_dict, code='invalid')
        return self.cleaned_data

    # validation: check after submit before save
    def clean_picture(self):
        # this is the current picture, nothing will happen if checkbox not clicked
        picture = self.cleaned_data['picture']
        # checkbox (False if clicked) -> return default picture
        if not picture:
            return 'picture/gdefault.gif'
        return picture


class MessageForm(ModelForm):
    # referencing Message model as basis for the form
    # initializing form input fields
    class Meta:
        model = Message
        fields = ['user', 'text',  'date', 'picture']

    # method to initialize the form
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop("user_id", None)
        super(MessageForm, self).__init__(*args, **kwargs)
        # set user input and date input type to hidden
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['date'].widget = forms.HiddenInput()
        # set visibility field

        # set text input type to textarea and add class 'form-control'
        self.fields['text'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'style': 'resize: none;'
        })

        self.fields['picture'].widget.attrs['accept'] = 'image/*'

    # return checked text input value
    def clean_text(self):
        text = self.cleaned_data['text']
        return text

    def save(self, commit=True, *args, **kwargs):
        instance = super(MessageForm, self).save(commit=False)
        instance.user = User.objects.get(pk=self.user_id)
        instance.date = datetime.datetime.now()
        if commit:
            instance.save()
        return instance


class FAQForm(ModelForm):
    other = forms.CharField(max_length=128, required=False)

    # referencing FAQ model as basis for the form
    # initializing form input fields
    class Meta:
        model = FAQ
        fields = ['author', 'question', 'category', 'answer']

    # method to initialize the form
    def __init__(self, *args, **kwargs):
        super(FAQForm, self).__init__(*args, **kwargs)
        self.categories = FAQ.objects.all().values('category').distinct()
        # set author initial value to current user, if not on admin page
        if 'instance' in kwargs:
            self.fields['author'].widget = forms.HiddenInput()
            user = kwargs.get('instance')
            self.fields['author'].initial = user.id
        # set question input type to text and add class and placeholder
        self.fields['question'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Frage'})
        # define question categories, set category input type to select and add categories as options
        # set answer input type to textarea, set size and placeholder
        self.fields['answer'].widget = forms.Textarea(attrs={
            'rows': '5',
            'placeholder': 'Antwort',
            'style': 'resize: none;'
        })
        # set class to 'form-control' for each input
        for field in self.fields:
            if field is 'other':
                self.fields[field].widget.attrs['class'] = 'form-control hidden'
                self.fields[field].widget.attrs['placeholder'] = 'Neue Kategorie eintragen ...'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        other = self.cleaned_data['other']
        error_dict = {}
        if other == 'Kategorie erstellen':
            error_dict['category'] = "Kategorie-Name nicht erlaubt!"
        if len(error_dict) > 0:
            raise ValidationError(error_dict, code='invalid')
        return self.cleaned_data

    def save(self, commit=True):
        instance = super(FAQForm, self).save(commit=False)
        if instance.category == 'Kategorie erstellen':
            instance.category = self.cleaned_data['other']
        if commit:
            instance.save()
        return instance
