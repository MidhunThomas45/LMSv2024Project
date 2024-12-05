from django.contrib import admin
from .models import Membership, UserMembership, Author, Category, Book, IssuedBook, ISBN, Language
# Register your models here.

admin.site.register(Membership)
admin.site.register(UserMembership)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(ISBN)
admin.site.register(Language)
admin.site.register(IssuedBook)