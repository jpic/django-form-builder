import autocomplete_light

from models import *

autocomplete_light.register(Author,
    add_another_url_name='admin:book_author_add')
autocomplete_light.register(Book,
    add_another_url_name='admin:book_book_add')
autocomplete_light.register(Publisher,
    add_another_url_name='admin:book_publisher_add')
