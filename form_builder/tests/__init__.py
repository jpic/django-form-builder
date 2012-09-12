import unittest

from django.test.client import Client
from django.contrib.contenttypes.models import ContentType

from book.models import Book
from ..models import Form, Tab, Field


class FormUpdateTest(unittest.TestCase):
    def test_001_create(self):
        client = Client()
        response = client.get('/forms/form/create/')
        self.failUnlessEqual(response.status_code, 200)

        response = client.post('/forms/form/create/', {
            'contenttype': ContentType.objects.get_for_model(Book).pk,
            'name': 'test form'})
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(response['Location'],
            'http://testserver/forms/form/1/update/')

    def test_002_update(self):
        client = Client()
        response = client.get('/forms/form/1/update/')
        self.failUnlessEqual(response.status_code, 200)

        fixture = """
[{
    "name": "a",
    "fields": [{
        "verbose_name": "authors",
        "help_text": "",
        "id": 4,
        "name": "authors",
        "kind": ""
    }, {
        "verbose_name": "aoeu",
        "help_text": "",
        "name": "aoeu",
        "kind": "django.db.models.fields.FloatField"
    }]
}, {
    "name": "e",
    "fields": [{
        "verbose_name": "name",
        "help_text": "",
        "id": 2,
        "name": "name",
        "kind": ""
    }, {
        "verbose_name": "publisher",
        "help_text": "",
        "id": 3,
        "name": "publisher",
        "kind": ""
    }]
}]
"""

        # check against a regression which caused fields to duplicate
        response = client.post('/forms/form/1/update/', {
            'form': fixture})
        response = client.post('/forms/form/1/update/', {
            'form': fixture})
        response = client.post('/forms/form/1/update/', {
            'form': fixture})

        self.failUnlessEqual(Form.objects.count(), 1)
        self.failUnlessEqual(Tab.objects.count(), 3)
        self.failUnlessEqual(Field.objects.count(), 5)
