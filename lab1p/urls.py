from django.urls import path
from . import views

urlpatterns = [
    # main
    path('', views.main, name='main'),

    # authors
    path('<int:author_pk>/', views.author_detail, name='author_detail'),
    path('authors/', views.authors, name='authors'),

    # books
    path('books/', views.books, name='books'),
    path('mybooks/', views.AddedBooksByUserListView, name='my-added'),
    path('book/<int:pk>/add/', views.addBookToCollections.as_view(), name='add-book'),  # to collection
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('book/<int:pk>/comment/', views.AddComment.as_view(), name='add-comment'),  # add comment for book

    # profile
    path('profile/', views.profile, name='user-detail'),
    path('profile/edit/', views.edit_full_profile, name='edit'),
    path('profile/editlog/<username>', views.update_log_profile, name='edit-login'),
    path('profile/collection/<int:pk>/edit/', views.edit_collection, name='edit-collection'),
    path('profile/collection/<int:pk>/delete/', views.DeleteCollection.as_view(), name='delete-collection'),
    path('profile/collection/<int:collection_id>/', views.books_for_collection, name='books-for-collection'),
    path('profile/collection/<int:collection_pk>/<int:book_pk>/', views.deleteBookFromCollection, name='delete-book'),

    # acc_management
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.UserRegister, name='register'),
    path('password_change', views.password_change, name='change_password'),
    path('password_reset', views.password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>', views.passwordResetConfirm, name='password_reset_confirm'),

    # features
    path('newcollection/', views.addCollection, name='add-collection'),  # user adds new collection
    path('charts/', views.charts, name='charts'),
    path('search/', views.search, name='search'),
    path('import/', views.importExcel, name='import'),
    path('export/', views.export_users_excel, name='export'),
]
