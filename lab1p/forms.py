from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, SetPasswordForm, \
    PasswordResetForm
from django.contrib.auth import get_user_model
from lab1p.models import UserProfile, Collection, Comment, Book


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}),
        label="Username")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email exists")

    def clean_username(self):
        data = self.cleaned_data['username']
        if not data.islower():
            raise forms.ValidationError("Usernames should be in lowercase")
        if '@' in data or '-' in data or '|' in data:
            raise forms.ValidationError("Usernames should not have special characters.")
        return data

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


# full login edit form
class EditUserProfileForm(UserChangeForm):
    password = None

    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        first = cleaned_data.get("first_name")
        second = cleaned_data.get("last_name")
        us = cleaned_data.get("username")

        for char in first:
            if not (char.isalpha()):
                raise forms.ValidationError("Fields must contain only letters")

        for char in second:
            if not (char.isalpha()):
                raise forms.ValidationError("Fields must contain only letters")

        for char in us:
            if not (char.isalpha()):
                raise forms.ValidationError("Fields must contain only letters")

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        first = cleaned_data.get("first_name")
        second = cleaned_data.get("last_name")

        for char in first:
            if not (char.isalpha()):
                raise forms.ValidationError("Fields must contain only letters")

        for char in second:
            if not (char.isalpha()):
                raise forms.ValidationError("Fields must contain only letters")


# only status edit form
class EditProfileForm(UserChangeForm):
    password = None

    status = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = (
            'status',
        )


class CollectionAddForm(forms.Form):
    Name = forms.CharField(max_length=50)
    Information = forms.CharField(max_length=150)

    def renew_collection_data(self):
        collection = Collection.create()

        collection.Name = self.cleaned_data['Name']
        collection.Information = self.cleaned_data['Information']

        return collection


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(help_text='A valid email address, please.', required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email exists")

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        self.clean()
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        return user


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'name',
            'text',
        )

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }


''' -- attempt to add book to collections form -- if works - delete
class AddBookForm(forms.ModelForm):

    collections = forms.ModelMultipleChoiceField(
                        queryset=None,
                        #queryset=Collection.user_coll.all(),
                        label="collections",
                        widget=forms.CheckboxSelectMultiple)

    def __init__(self, collections, *args, **kwargs):
        #self.request = kwargs.pop('request')
        super(AddBookForm, self).__init__(*args, **kwargs)
        self.fields['collections'].queryset = collections

    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_data['collections'] = cleaned_data['collections']
        return self.cleaned_data
    
    class Meta:
        model = Book
        fields = (
            'collections',
        )
        exclude =(
            'title',
            'author',
            'isbn',
            'genre',
            'Information',
            'adder',
        )
'''


class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, collection):
        return "%s" % collection.Name


class AddBForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(AddBForm, self).__init__(*args, **kwargs)
        self.fields['collections'].queryset = Collection.objects.filter(
            creator=self.request.user)

    class Meta:
        model = Book
        fields = ['collections']

    collections = CustomModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple
    )


class StPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', ['new_password2']]


class PasswordReset(PasswordResetForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', ['new_password2']]
