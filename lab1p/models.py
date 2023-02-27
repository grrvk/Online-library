from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError


class Author(models.Model):
    Name = models.CharField(max_length=30)
    Surname = models.CharField(max_length=30)
    Bio = models.CharField(max_length=200, default='No bio', blank=True)

    def __str__(self):
        return f'{self.Name} {self.Surname}'

    def clean(self):
        for char in self.Name:
            if not (char.isalpha() or char == ' '):
                raise ValidationError("Name must not have numbers or symbols")
        for char in self.Surname:
            if not (char.isalpha() or char == ' '):
                raise ValidationError("Surname must not have numbers or symbols")

    class Meta:
        unique_together = ("Name", "Surname")
        ordering = ['Name', 'Surname']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])


class Genre(models.Model):
    Name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.Name

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    @classmethod
    def create(cls, Name):
        genre = cls(Name=Name)
        return genre

    def clean(self):
        for char in self.Name:
            if not (char.isalpha() or char == ' '):
                raise ValidationError("Genre must not have numbers or symbols")

    display_genre.short_description = 'Genre'


#class CollectionManager(models.Manager):
 #   def get_queryset(self):
  #      return super().get_queryset().filter(creator=2)


class Collection(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections', null=True)
    Name = models.CharField(max_length=50, default='To read')
    Information = models.CharField(max_length=150, default='', blank=True)
    date_created = models.DateField(null=True, blank=True)
    #user_coll = CollectionManager()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(creator=self.request.user)

    def __str__(self):
        return f'{self.Name} - by {self.creator.username}'

    class Meta:
        unique_together = ("creator", "Name")

    def get_absolute_url(self):
        return reverse('collection-detail', args=[str(self.id)])

    def clean(self):
        for char in self.Name:
            if not (char.isalpha() or char == ' '):
                raise ValidationError("Name of collection must not have numbers or symbols")

    @classmethod
    def create(cls, creator, name, info):
        collection = cls(creator=creator, Name=name, Information=info)
        return collection


def create_toread(sender, **kwargs):
    if kwargs['created']:
        collection = Collection.objects.create(creator=kwargs['instance'])


post_save.connect(create_toread, sender=User)


class Book(models.Model):
    # must add validators [**options]
    title = models.CharField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='auth_books')
    isbn = models.CharField('ISBN', max_length=13, unique=True, default='')
    genre = models.ManyToManyField(Genre, related_name='books', blank=True)
    Information = models.TextField(blank=True, max_length=1000)
    adder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    collections = models.ManyToManyField(Collection, blank=True, related_name='books_for_collecton')

    # must add validators [**options]

    def clean(self):
        try:
            num = int(self.isbn)
            if len(self.isbn) != 13:
                raise ValidationError("ISBN must be 13 symbols long")
            for char in self.title:
                if not (char.isalpha() or char == ' ' or char == '-'):
                    raise ValidationError("Name of book must not have numbers")
        except ValueError:
            raise ValidationError("ISBN must have only numbers")

    def __str__(self):
        return self.title

    @classmethod
    def create(cls, title, author, isbn):
        book = cls(title=title, author=author, isbn=isbn)
        return book

    class Meta:
        unique_together = ("title", "author")

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    status = models.CharField(max_length=250, default='', blank=True)
    bio = models.CharField(max_length=250, default='', blank=True)
    books = models.ManyToManyField(Book, blank=True, related_name='profile_f_books')

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('user-detail', args=[str(self.id)])


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])


post_save.connect(create_profile, sender=User)


class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    text = models.TextField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    def clean(self):
        for char in self.name:
            if not (char.isalpha() or char == ' ' or char == '-'):
                raise ValidationError("Name of comment must not have numbers")

    def __str__(self):
        return '%s - %s' % (self.book.title, self.name)
