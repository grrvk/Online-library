from django.contrib import admin

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.site, name='main'),
    path('index/', views.index, name='index'),     #latest authors
    path('<int:author_pk>/', views.author_detail, name='author_detail'),
    path('books/', views.books, name='books'),
    path('authors/', views.authors, name='authors'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('mybooks/', views.AddedBooksByUserListView, name='my-added'),
    path('profile/', views.profile, name='user-detail'),
    path('profile/edit/', views.edit_full_profile, name='edit'),
    path('profile/editlog/', views.UserLoginIfoEdit.as_view(), name='edit-login'),
    path('profile/collection/<int:collection_id>/', views.books_for_collection, name='books-for-collection'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('newcollection/', views.addCollection, name='add-collection'),
    path('book/<int:pk>/comment/', views.AddComment.as_view(), name='add-comment'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/collection/<int:pk>/delete/', views.DeleteCollection.as_view(), name='delete-collection'),
    path('book/<int:pk>/add/', views.bTcoll.as_view(), name='add-book'),
    path('profile/collection/<int:pk>/edit/', views.edit_collection, name='edit-collection'),
    path('profile/collection/<int:collection_pk>/<int:book_pk>/', views.deleteBookFromCollection, name='delete-book'),
    path('charts/', views.charts, name='charts'),
    path('search/', views.search, name='search'),
    path('import/', views.importExcel, name='import'),
    path('export/', views.export_users_excel, name='export'),
]
