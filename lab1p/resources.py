from import_export import resources
from .models import Author, Book, Genre


class AuthorResource(resources.ModelResource):
    class meta:
        model = Author


class BookResource(resources.ModelResource):
    class meta:
        model = Book


class GenreResource(resources.ModelResource):
    class meta:
        model = Genre