from django import forms

from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.safestring import mark_safe

from .models import User, UserProfile, Message, FAQ, GroupProfile


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


# form to update user's account information
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

    # method to save user's updated information
    # 'set_password' is for encoding raw text password
    def save(self, commit=True):
        instance = super(UserForm, self).save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            instance.set_password(password)
        if commit:
            instance.save()
        return instance


# form to update user's personal information
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
        # set studentNumber type to text
        self.fields['studentNumber'].widget = forms.TextInput()
        # set academicDiscipline type to select and fill with AD_CHOICES
        self.fields['academicDiscipline'].widget = forms.Select(choices=AD_CHOICES)

        # for each field set class to 'form-control' except 'picture',
        # set class to 'checkNumeric' for studentNumber and
        # set initial value to user's personal information
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


class GroupProfileForm(ModelForm):
    ack_password = forms.CharField(max_length=128, widget=forms.PasswordInput, required=False)

    class Meta:
        model = GroupProfile
        fields = ['name', 'short', 'desc', 'password', 'picture']
        widgets = {
            'desc': forms.Textarea(attrs={'rows': 4}),
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super(GroupProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'picture':
                self.fields[field].widget.attrs['class'] = 'form-control'


class GroupProfileEditForm(ModelForm):
    ack_password = forms.CharField(max_length=128, required=False)

    class Meta:
        model = GroupProfile
        fields = ['name', 'short', 'desc', 'password', 'picture']
        widgets = {
            'desc': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        print(instance.password)
        super(GroupProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['short'].widget.attrs['readonly'] = True  # set username input readonly
        self.fields['ack_password'].initial = instance.password
        for field in self.fields:
            if field != 'picture':
                self.fields[field].widget.attrs['class'] = 'form-control'

    # method to compare password and password confirmation input values
    # if equal: return password
    # else: return error message
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

    # validation: check after submit before save
    def clean_picture(self):
        # this is the current picture, nothing will happen if checkbox not clicked
        picture = self.cleaned_data.get('picture')
        # checkbox (False if clicked) -> return default picture
        if picture == False:
            return 'picture/gdefault.gif'
        return picture


# form to add a new message
class MessageForm(ModelForm):
    # referencing Message model as basis for the form
    # initializing form input fields
    class Meta:
        model = Message
        fields = ['user', 'text',  'date', 'picture']

    # method to initialize the form
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        # set user input and date input type to hidden
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['date'].widget = forms.HiddenInput()
        # set visibility field
        
        # set text input type to textarea and add class 'form-control'
        self.fields['text'].widget = forms.Textarea(attrs=self.fields['text'].widget.attrs)
        self.fields['text'].widget.attrs['class'] = 'form-control'
        self.fields['text'].widget.attrs['rows'] = '5'

    # return checked text input value
    def clean_text(self):
        text = self.cleaned_data.get('text')
        return text


class FAQForm(ModelForm):
    # referencing FAQ model as basis for the form
    # initializing form input fields
    class Meta:
        model = FAQ
        fields = ['author', 'question', 'category', 'answer']

    # method to initialize the form
    def __init__(self, *args, **kwargs):
        super(FAQForm, self).__init__(*args, **kwargs)
        # set author initial value to current user, if not on admin page
        if 'instance' in kwargs:
            self.fields['author'].widget = forms.HiddenInput()
            user = kwargs.get('instance')
            self.fields['author'].initial = user.id
        # set question input type to text and add class and placeholder
        self.fields['question'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Frage'})
        # define question categories, set category input type to select and add categories as options
        catChoices = (
            ('Allgemeine Frage', 'Allgemeine Frage'),
            ('Startseite', 'Startseite'),
            ('Profilseite', 'Profilseite'),
            ('Gruppenseite', 'Gruppenseite'),
            ('Gruppeneinstellungen', 'Gruppeneinstellungen'),
            ('Infoseite', 'Infoseite'),
            ('Suche', 'Suche'),
            ('Einstellungen', 'Einstellungen'),
            ('Benachrichtigungen', 'Benachrichtigungen'),
            ('Nachrichtenanzeige', 'Nachrichtenanzeige')
        )
        self.fields['category'] = forms.ChoiceField(choices=catChoices, widget=forms.Select)
        # set answer input type to textarea, set size and placeholder
        self.fields['answer'].widget = forms.Textarea(attrs={'rows': '5', 'placeholder': 'Antwort'})
        # set class to 'form-control' for each input
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
