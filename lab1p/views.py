from zipfile import BadZipFile

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpRequest, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, DeleteView, UpdateView
from django.contrib import messages

from .models import Author, Book, Genre, UserProfile, Collection, Comment
from django.views import generic
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth import logout, login
from tablib import Dataset
import xlwt
from lab1p.forms import EditProfileForm, EditUserProfileForm, CollectionAddForm, CommentForm, \
    UserRegisterForm, AddBForm, UserLoginForm, UserUpdateForm, StPasswordForm, PasswordReset, RegistrationForm
from .tokens import account_activation_token

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage


# main


def main(request):
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


# authors


def author_detail(request, author_pk):
    author = get_object_or_404(Author, pk=author_pk)
    authBooks = Book.objects.filter(author=author)

    context = {
        'author': author,
        'books': authBooks,
    }

    return render(request, 'lab1p/../templates/author.html', context)


def authors(request):
    all_authors = Author.objects.all()
    return render(request=request, template_name="templates/authors.html", context={"authors_obj": all_authors})


# books


def books(request):  # all-books page + adding to LIKED
    if request.method == "POST":
        book_pk = request.POST.get("book_pk")
        book = Book.objects.get(id=book_pk)
        request.user.profile.books.add(book)
        messages.success(request, f'{book} added to liked')
        return redirect('books')
    all_books = Book.objects.all()
    return render(request=request, template_name="templates/books.html", context={"books_obj": all_books})


def AddedBooksByUserListView(request):  # my LIKED - rename
    user_profile = UserProfile.objects.get(user=request.user)
    all_books = user_profile.books.all()

    context = {
        'book_list': all_books,
    }
    return render(request, 'lab1p/book_list_added_user.html', context)


class addBookToCollections(UpdateView):
    model = Book
    form_class = AddBForm
    template_name = 'templates/add_book.html'
    success_url = reverse_lazy('main')

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(addBookToCollections, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class BookDetailView(generic.DetailView):
    model = Book


class AddComment(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'templates/add_comment.html'

    def form_valid(self, form):
        form.instance.book_id = self.kwargs['pk']
        form.instance.user_id = self.request.user.id
        return super().form_valid(form)

    success_url = reverse_lazy('main')


# profile


def profile(request):
    creator = request.user
    collections = creator.collections.all()
    context = {
        'user': creator,
        'collection': collections
    }
    return render(request, 'templates/profile.html', context)


def edit_full_profile(request):  # EDIT PROFILE FUNC - not login info
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


# login info edit - now is not used -- commented GET_OBJECT  -- if works - delete
class UserLoginIfoEdit(generic.UpdateView):
    form_class = EditUserProfileForm
    template_name = 'templates/edit_login_info.html'
    success_url = reverse_lazy('main')

    # def get_object(self):
    #    return self.request.user


def edit_collection(request, pk):
    collection = Collection.objects.get(pk=pk)
    books_obj = Book.objects.filter(collections=collection)
    context = {
        'collection': collection,
        'books_obj': books_obj,
    }
    return render(request, 'templates/edit_collection.html', context=context)


class DeleteCollection(DeleteView):
    model = Collection
    template_name = 'templates/delete_collection.html'
    success_url = reverse_lazy('edit')


def books_for_collection(request, collection_id):
    collection = Collection.objects.get(id=collection_id)
    all_books = Book.objects.filter(collections=collection)

    context = {
        'collection': collection,
        'book_list': all_books,
    }
    return render(request, 'lab1p/book_list_for_collection.html', context)


def deleteBookFromCollection(request, collection_pk, book_pk):
    book = Book.objects.get(pk=book_pk)
    collection = Collection.objects.get(pk=collection_pk)

    if request.method == 'GET':
        return render(request, 'templates/delete_book_from_cl.html', {'book': book})
    elif request.method == 'POST':
        book.collections.remove(collection)
        messages.success(request, 'The book has been deleted successfully.')
        return redirect('user-detail')


# acc_management


def logout_view(request):
    logout(request)
    return redirect('main')


''' ---register trial - if works - delete
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
'''


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('main')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('main')


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("registration/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, please go to you email {to_email} inbox and click on \
                received activation link to confirm and complete the registration.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')


# commented GET_OBJECT -- if works - delete
def UserRegister(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('main')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = RegistrationForm()

    return render(
        request=request,
        template_name="registration/registration_form.html",
        context={"form": form}
    )
    # def get_object(self):
    #    return self.request.user


def custom_login(request):
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("main")

        else:
            for key, error in list(form.errors.items()):

                messages.error(request, error)

    form = UserLoginForm()

    return render(
        request=request,
        template_name="registration/login.html",
        context={"form": form}
    )


def update_log_profile(request, username):
    if request.method == "POST":
        user = request.user
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                form.clean()
                user_form = form.save()
            except Exception as e:
                messages.error(request, f'Error: {e}')
            messages.success(request, f'{user_form.username}, Your profile has been updated!')
            return redirect("main")

        for error in list(form.errors.values()):
            messages.error(request, error)

    user = get_user_model().objects.filter(username=username).first()
    form = UserUpdateForm(instance=user)
    return render(
            request=request,
            template_name="templates/edit_login_info.html",
            context={"form": form}
        )


@login_required
def password_change(request):
    user = request.user
    if request.method == "POST":
        form = StPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password was updated')
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    form = StPasswordForm(user)
    return render(request, 'registration/password_reset_confirm.html', {'form': form})


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordReset(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("registration/template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                        <h2>Password reset sent</h2><hr>
                        <p>
                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                            You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address 
                            you registered with, and check your spam folder.
                        </p>
                        """
                    )
                else:
                    messages.error(request, "Problem sending reset password email, SERVER PROBLEM")

            return redirect('main')

    form = PasswordReset()
    return render(
        request=request,
        template_name="registration/password_reset.html",
        context={"form": form}
        )


def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = StPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and log in now.")
                return redirect('main')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = StPasswordForm(user)
        return render(request, 'registration/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("main")


# features


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


def charts(request):
    genres = Genre.objects.all()
    al_genres = Genre.objects.all()
    all_authors = Author.objects.all()
    nums_f_genres = []
    nums_f_authors = []
    for genre in al_genres:
        nums_f_genres.append(genre.books.count())
    for author in all_authors:
        nums_f_authors.append(author.auth_books.count())
    context = {
        'genres': genres,
        'authors': all_authors,
        'nums': nums_f_genres,
        'auth_nums': nums_f_authors,
    }
    return render(request, 'templates/charts.html', context)


def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        genres = Genre.objects.filter(Name__contains=searched)
        searched_books_names = (Book.objects.filter(title__contains=searched) |
                                Book.objects.filter(genre__Name__contains=searched) |
                                Book.objects.filter(author__Name__contains=searched) |
                                Book.objects.filter(author__Surname__contains=searched)).distinct()

        print(searched_books_names)
        context = {
            'search': searched,
            'books_names': searched_books_names,
        }
        return render(request, 'templates/search_page.html', context)
    else:
        return render(request, 'templates/search_page.html')


# commented some unused vars -- if works - delete
def importExcel(request):
    if request.method == 'POST':
        # author_res = AuthorResource()
        # book_res = BookResource()
        # genre_res = GenreResource
        dataset = Dataset()
        new_authors = request.FILES['file']
        # new_books = request.FILES['file']
        imported_data = ''
        try:
            imported_data = dataset.load(new_authors.read(), format='xls')
        except Exception as e:
            messages.warning(request, f"Error {e} for the book with id {e}")
            print(f"exception {e}")
            # finish def
        error_messages = []
        for index, data in enumerate(imported_data):
            latest_id = Author.objects.all().values_list('id', flat=True).order_by('-id').first()
            if latest_id is None:
                latest_id = 0
            # latest_id_genre = Genre.objects.all().values_list('id', flat=True).order_by('-id').first()

            if not Author.objects.filter(Name=data[1], Surname=data[2]):
                value = Author(
                    latest_id + 1,
                    data[1],
                    data[2],
                    data[3],
                )
                try:
                    value.clean()
                    value.save()
                except Exception as e:
                    messages.warning(request, f"Error {e} for the book with id ")

            try:
                author = Author.objects.get(Name=data[1], Surname=data[2])
                author.clean()
            except Exception as e:
                messages.warning(request, f"Error {e} for the author with id {data[0]}. Data of "
                                          f"this row was ignored. ")

            import_books = Book.objects.all()
            unique = True
            print(data[6])
            for book in import_books:
                if book.isbn == data[6]:
                    unique = False
            if not unique:
                book = Book.objects.get(isbn=data[6])
                if book.title == data[5] and book.author == author:
                    genres = Genre.objects.all()
                    for i in range(7, 10):
                        if data[i] != '':
                            unique_two = True
                            for genre in genres:
                                if genre.Name == data[i]:
                                    unique_two = False
                            genre_new = None
                            if unique_two:
                                try:
                                    genre_new = Genre.create(Name=data[i])
                                    genre_new.save()
                                except Exception as e:
                                    messages.warning(request, f"Error {e} for the book with id {data[4]}")
                            else:
                                genre_new = Genre.objects.get(Name=data[i])
                            book.genre.add(genre_new)
                else:
                    messages.warning(request, f"There is another book with the same isbn as the book with "
                                              f"id {data[4]}. Data was ignored.")

            else:
                if not Book.objects.filter(title=data[5], author=author):
                    try:
                        book = Book.create(data[5], author, data[6])
                        book.save()
                    except Exception as e:
                        messages.warning(request, f"Error {e} for the book with id {data[4]}")
                    genres = Genre.objects.all()
                    for i in range(7, 10):
                        if data[i] != '':
                            unique_two = True
                            for genre in genres:
                                if genre.Name == data[i]:
                                    unique_two = False
                            if unique_two:
                                try:
                                    genre_new = Genre.create(Name=data[i])
                                    genre_new.save()
                                except Exception as e:
                                    messages.warning(request, f"Error {e} for the book with id {data[4]}")
                            else:
                                genre_new = Genre.objects.get(Name=data[i])
                            book.genre.add(genre_new)
                    book.save()
                else:
                    messages.warning(request, f"There is already a book with the the same name and author as book "
                                              f"with id {data[4]}. Data was ignored.")

    return render(request, 'templates/import.html')


def export_users_excel(request):
    if request.method == 'POST':
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Data.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Data')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['id_author', 'Name', 'Surname', 'Bio', 'id_book', 'title', 'isbn', 'genre1',
                   'genre2', 'genre3']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        books_export = Book.objects.all()

        for book in books_export:
            row_num += 1
            info = [book.author_id, book.author.Name, book.author.Surname, book.author.Bio, book.id, book.title,
                    book.isbn]
            genres = book.genre.all()[:3]
            for genre in genres:
                info.append(genre.Name)
            for col_num in range(len(info)):
                ws.write(row_num, col_num, str(info[col_num]), font_style)
        wb.save(response)

        return response

    return render(request, 'templates/export.html')


''' profile editing - if works - delete (only status)
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
'''

''' profile editing (BUT FORM) - if works - delete (only status)
class UserEditProfile(generic.UpdateView):
    form_class = EditProfileForm
    template_name = 'templates/edit_profile.html'
    success_url = reverse_lazy('main')

    def get_object(self):
        return self.request.user
'''

''' --- full login info edit -- if works - delete
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
'''

''' ----- previous attempt to add books to collections -- if works - delete
def addBookToColl(request, pk):
    def get_form_kwargs(self):
        kwargs = super(AddBookForm, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    book = Book.objects.get(pk=pk)
    collections = Collection.objects.filter(creator=request.user)
    form = AddBookForm(collections)
    print(form.errors)
    print(form.is_valid())
    if request.method == 'POST':
        form = AddBookForm(collections)
        print(form.errors)
        print(form.is_valid())
        form.save(commit=False)
        form.save_m2m()
        return redirect('main')
    context = {'form': form}
    return render(request, 'templates/add_book.html', context)
'''
