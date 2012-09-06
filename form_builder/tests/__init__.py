import unittest

from django.contrib.contenttypes.models import ContentType

from book.models import Book
from ..models import Form, Tab, Field


class FormUpdateTest(unittest.TestCase):
    def test_001_name_to_info(self):
        form = Form(name='My Form',
            contenttype=ContentType.objects.get_for_model(Book))
        form.save()

        name = Field.objects.get(tab__form=form, name='name')

        data = [
            {
                'fields': [
                    {
                        'help_text': '',
                        'model_field_name': 'name',
                        'name': 'name',
                        'id': name.pk,
                    },
                ],
                'name': 'Info',
            }
        ]

        form.update_from_dict(data)


        self.assertEqual()
