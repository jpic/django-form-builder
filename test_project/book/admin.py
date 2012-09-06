from django.contrib import admin

import autocomplete_light

from models import *


class BookAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Book)

admin.site.register(Author)
admin.site.register(Book, BookAdmin)
admin.site.register(Publisher)
