from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.core.exceptions import ValidationError
from django.contrib import messages


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Row, Column, Field

from lab1p.models import UserProfile, Collection, Comment, Author, Book, Genre


class AuthorForm(forms.Form):
    class Meta:
        model = Author
        fields = '__all__'


class BookForm(forms.Form):
    class Meta:
        model = Book
        fields = (
            'title',
            'isbn',
        )


class GenreForm(forms.Form):
    class Meta:
        model = Genre
        fields = (
            'Name',
        )


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
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


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


class AddBookForm(forms.ModelForm):

    collections = forms.ModelMultipleChoiceField(
                        queryset=Collection.objects.all().order_by('Name'),
                        #queryset=Collection.user_coll.all(),
                        label="Collections",
                        widget=forms.CheckboxSelectMultiple)

    def __init__(self, user, *args, **kwargs):
        #self.creator_id = kwargs.pop(user)
        super(AddBookForm, self).__init__(*args, **kwargs)
        self.fields['collections'].queryset = user

    class Meta:
        model = Book
        fields = (
            'collections',
        )




