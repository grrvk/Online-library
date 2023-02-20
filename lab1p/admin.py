from django.contrib import admin
from .models import Author, Genre, Book, Collection, UserProfile, Comment


# Register your models here.
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('Name', 'Surname')


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')


class CollectionAdmin(admin.ModelAdmin):
    list_filter = ('Name', 'date_created')
    list_display = ('Name', 'creator')
    fieldsets = (
        (None, {
            'fields': ('Name', 'creator')
        }),
        ('Optional', {
            'fields': ('Information', 'date_created')
        }),
    )


admin.site.site_url = "/lab1p"

admin.site.register(UserProfile)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(Book, BookAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Comment)
