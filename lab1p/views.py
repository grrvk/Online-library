from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView
from django.contrib import messages
from pandas.io import parsers

from .models import Author, Book, Genre, UserProfile, Collection, Comment
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from tablib import Dataset
import xlwt
from rest_framework import generics
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from .resources import AuthorResource, BookResource, GenreResource

from django.conf import settings
from django.core.files.storage import FileSystemStorage

import csv

from lab1p.forms import RegistrationForm, EditProfileForm, EditUserProfileForm, CollectionAddForm, CommentForm, \
    UserRegisterForm, AddBookForm, AuthorForm, BookForm
from django.core.exceptions import ValidationError


# Create your views here.

def logout_view(request):
    logout(request)

    return redirect('main')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main')
    else:
        form = RegistrationForm()
        args = {'form': form}
        return render(request, 'registration/registration_form.html', args)


class UserRegister(generic.CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('main')

    def get_object(self):
        return self.request.user


def index(request):
    latest_author_list = Author.objects.order_by('-Name')[:5]
    context = {
        'latest_author_list': latest_author_list,
    }
    return render(request, 'lab1p/../templates/index.html', context)


def author_detail(request, author_pk):
    author = get_object_or_404(Author, pk=author_pk)

    books = Book.objects.filter(author=author)

    context = {
        'author': author,
        'books': books,
    }

    return render(request, 'lab1p/../templates/author.html', context)


def charts(request):
    genres = Genre.objects.all()
    al_books = Book.objects.all()
    all_authors = Author.objects.all()
    nums_f_genres = []
    nums_f_authors = []
    for book in al_books:
        nums_f_genres.append(book.genre.count())
    for author in all_authors:
        nums_f_authors.append(author.auth_books.count())
    context = {
        'genres': genres,
        'authors': all_authors,
        'nums': nums_f_genres,
        'auth_nums': nums_f_authors,
    }
    return render(request, 'templates/charts.html', context)


def profile(request):
    creator = request.user
    collections = creator.collections.all()
    context = {
        'user': creator,
        'collection': collections
    }
    return render(request, 'templates/profile.html', context)


def edit_profile(request, user_id):
    user = get_object_or_404(get_user_model(), pk=user_id)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return redirect('main')
    else:
        form = EditProfileForm(instance=user)
        args = {'form': form}
        return render(request, 'templates/edit_profile.html', args)


class UserEditProfile(generic.UpdateView):
    form_class = EditProfileForm
    template_name = 'templates/edit_profile.html'
    success_url = reverse_lazy('main')

    def get_object(self):
        return self.request.user


def edit_full_profile(request):
    creator = request.user
    collections = creator.collections.all()
    form = EditProfileForm(request.POST or None, instance=creator.profile)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=creator.profile)
        if form.is_valid():
            messages.success(request, 'Status changed')
            form.save()
    context = {
        'form': form,
        'collections': collections,
    }
    return render(request, 'templates/edit_profile.html', context=context)


class DeleteCollection(DeleteView):
    model = Collection
    template_name = 'templates/delete_collection.html'
    success_url = reverse_lazy('edit')


def deleteBookFromCollection(request, collection_pk, book_pk):
    book = Book.objects.get(pk=book_pk)
    collection = Collection.objects.get(pk=collection_pk)

    if request.method == 'GET':
        return render(request, 'templates/delete_book_from_cl.html', {'book': book})
    elif request.method == 'POST':
        book.collections.remove(collection)
        messages.success(request, 'The book has been deleted successfully.')
        return redirect('user-detail')


def edit_collection(request, pk):
    collection = Collection.objects.get(pk=pk)
    books_obj = Book.objects.filter(collections=collection)
    context = {
        'collection': collection,
        'books_obj': books_obj,
    }
    return render(request, 'templates/edit_collection.html', context=context)


def edit_login_info(request, user_id):
    user = get_object_or_404(get_user_model(), pk=user_id)
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return redirect('main')

    else:
        form = EditUserProfileForm(instance=user)
        args = {'form': form}
        return render(request, 'templates/edit_login_info.html', args)


class UserLoginIfoEdit(generic.UpdateView):
    form_class = EditUserProfileForm
    template_name = 'templates/edit_login_info.html'
    success_url = reverse_lazy('main')

    def get_object(self):
        return self.request.user


def site(request):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    num_books = Book.objects.all().count()
    num_authors = Author.objects.all().count()
    num_genres = Genre.objects.all().count()

    user = get_user_model()
    num_users = user.objects.all().count()

    latest_author_list = Author.objects.order_by('-Name')[:5]
    context = {
        'num_authors': num_authors,
        'latest_author_list': latest_author_list,
        'num_books': num_books,
        'num_genres': num_genres,
        'num_users': num_users,
        'num_visits': num_visits,
    }
    return render(request, 'lab1p/../templates/main.html', context)


class BookListView(generic.ListView):
    model = Book


class BookDetailView(generic.DetailView):
    model = Book


def books(request):
    if request.method == "POST":
        book_pk = request.POST.get("book_pk")
        book = Book.objects.get(id=book_pk)
        request.user.profile.books.add(book)
        messages.success(request, (f'{book} added to liked'))
        return redirect('books')
    all_books = Book.objects.all()
    return render(request=request, template_name="templates/books.html", context={"books_obj": all_books})


def authors(request):
    all_authors = Author.objects.all()
    return render(request=request, template_name="templates/authors.html", context={"authors_obj": all_authors})


def AddedBooksByUserListView(request):
    user_profile = UserProfile.objects.get(user=request.user)
    all_books = user_profile.books.all()

    context = {
        'book_list': all_books,
    }
    return render(request, 'lab1p/book_list_added_user.html', context)


def books_for_collection(request, collection_id):
    collection = Collection.objects.get(id=collection_id)
    all_books = Book.objects.filter(collections=collection)

    context = {
        'collection': collection,
        'book_list': all_books,
    }
    return render(request, 'lab1p/book_list_for_collection.html', context)


class AddComment(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'templates/add_comment.html'

    def form_valid(self, form):
        form.instance.book_id = self.kwargs['pk']
        form.instance.user_id = self.request.user.id
        return super().form_valid(form)

    success_url = reverse_lazy('main')


def addCollection(request):
    if request.method == 'POST':
        form = CollectionAddForm(request.POST)
        if form.is_valid():
            collection = Collection.create(request.user, form.cleaned_data['Name'], form.cleaned_data['Information'])
            collection.save()
            return redirect('main')

    else:
        form = CollectionAddForm()
        args = {'form': form}
        return render(request, 'registration/collection_form.html', args)


def addBookToColl(request, pk):
    book = Book.objects.get(pk=pk)
    collections = Collection.objects.filter(creator=request.user)

    form = AddBookForm(collections)
    if request.POST and form.is_valid():
        form = AddBookForm(collections)
        form.save(commit=False)
        form.save_m2m()
        return redirect('main')

    context = {'form': form}
    return render(request, 'templates/add_book.html', context)


def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        books_names = Book.objects.filter(title__contains=searched)
        books_genres = Book.objects.filter(genre__Name__contains=searched)
        authors = Author.objects.filter(Name__contains=searched) | Author.objects.filter(Surname__contains=searched)

        context = {
            'search': searched,
            'books_names': books_names,
            'books_genres': books_genres,
            'authors': authors,
        }
        return render(request, 'templates/search_page.html', context)
    else:
        return render(request, 'templates/search_page.html')


def importExcell(request):
    if request.method == 'POST':
        author_res = AuthorResource()
        dataset = Dataset()
        new_authors = request.FILES['file']
        imported_data = dataset.load(new_authors.read(), format='xlsx')
        for data in imported_data:
            latest_id = Author.objects.all().values_list('id', flat=True).order_by('-id').first()
            value = Author(
                latest_id + 1,
                data[1],
                data[2],
                data[3],
            )
            if (not Author.objects.filter(Name=data[1], Surname=data[2])):
                value.save()

    return render(request, 'templates/import.html')


def importExcel(request):
    if request.method == 'POST':
        author_res = AuthorResource()
        book_res = BookResource()
        genre_res = GenreResource
        dataset = Dataset()
        new_authors = request.FILES['file']
        new_books = request.FILES['file']
        imported_data = dataset.load(new_authors.read(), format='xlsx')
        for data in imported_data:
            latest_id = Author.objects.all().values_list('id', flat=True).order_by('-id').first()
            if (latest_id == None):
                latest_id = 0;
            latest_id_genre = Genre.objects.all().values_list('id', flat=True).order_by('-id').first()

            if (not Author.objects.filter(Name=data[1], Surname=data[2])):
                value = Author(
                    latest_id + 1,
                    data[1],
                    data[2],
                    data[3],
                )
                value.save()

            author = Author.objects.get(Name=data[1], Surname=data[2])

            books = Book.objects.all()
            unique = True
            for book in books:
                if (book.isbn == data[6]):
                    unique = False;

            if (not unique):
                book = Book.objects.get(isbn=data[6])
                if (book.title == data[5] and book.author == author):
                    genres = Genre.objects.all()
                    for i in range(7, 10):
                        if (data[i] is not None):
                            unique_two = True
                            for genre in genres:
                                if (genre.Name == data[i]):
                                    unique_two = False;
                            if (unique_two):
                                genre_new = Genre.create(Name=data[i])
                                genre_new.save()
                            else:
                                genre_new = Genre.objects.get(Name=data[i])
                            book.genre.add(genre_new)
                else:
                    messages.warning(request, 'ISBN of some books is not unique. Please check the uploading data.')
            else:
                if (not Book.objects.filter(title=data[5], author=author)):
                    book = Book.create(data[5], author, data[6])
                    book.save()
                    genres = Genre.objects.all()
                    for i in range(7, 10):
                        if (data[i] is not None):
                            unique_two = True
                            for genre in genres:
                                if (genre.Name == data[i]):
                                    unique_two = False;
                            if (unique_two):
                                genre_new = Genre.create(Name=data[i])
                                try:
                                    genre_new.save()
                                except:
                                    pass
                            else:
                                genre_new = Genre.objects.get(Name=data[i])
                            book.genre.add(genre_new)
                        book.save()

            # якщо книги немає - створюю, якщо є - дані не перезаписую. Чи треба?

    return render(request, 'templates/import.html')


def export_users_excel(request):
    if request.method == 'POST':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Data.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Data')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['id_author', 'Name', 'Surname', 'Bio', 'id_book', 'title', 'isbn', 'genre1', 'genre2', 'genre3']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        books = Book.objects.all()

        for book in books:
            row_num += 1
            col_num = 0
            ws.write(row_num, col_num, str(book.author_id), font_style)
            col_num += 1
            ws.write(row_num, col_num, str(book.author.Name), font_style)
            col_num += 1
            ws.write(row_num, col_num, str(book.author.Surname), font_style)
            col_num += 1
            ws.write(row_num, col_num, str(book.author.Bio), font_style)
            col_num += 1
            ws.write(row_num, col_num, str(book.id), font_style)
            col_num += 1
            ws.write(row_num, col_num, str(book.title), font_style)
            col_num += 1
            ws.write(row_num, col_num, str(book.isbn), font_style)
            genres = book.genre.all()[:3]
            for genre in genres:
                col_num += 1
                ws.write(row_num, col_num, str(genre.Name), font_style)

        wb.save(response)

        return response

    return render(request, 'templates/export.html')
