from __future__ import unicode_literals

import warnings

from django.core import management
from django.db import transaction
from django.test import TestCase, TransactionTestCase

from .models import Article, Book


class SampleTestCase(TestCase):
    fixtures = ['fixture1.json', 'fixture2.json']

    def testClassFixtures(self):
        "Test cases can load fixture objects into models defined in packages"
        self.assertEqual(Article.objects.count(), 3)
        self.assertQuerysetEqual(
            Article.objects.all(),[
                "Django conquers world!",
                "Copyright is fine the way it is",
                "Poker has no place on ESPN",
            ],
            lambda a: a.headline
        )


class TestNoInitialDataLoading(TransactionTestCase):
    def test_syncdb(self):
        transaction.set_autocommit(False)
        try:
            Book.objects.all().delete()

            management.call_command(
                'syncdb',
                verbosity=0,
                load_initial_data=False
            )
            self.assertQuerysetEqual(Book.objects.all(), [])
            transaction.rollback()
        finally:
            transaction.set_autocommit(True)


    def test_flush(self):
        # Test presence of fixture (flush called by TransactionTestCase)
        self.assertQuerysetEqual(
            Book.objects.all(), [
                'Achieving self-awareness of Python programs'
            ],
            lambda a: a.name
        )

        transaction.set_autocommit(False)
        try:
            management.call_command(
                'flush',
                verbosity=0,
                interactive=False,
                commit=False,
                load_initial_data=False
            )
            self.assertQuerysetEqual(Book.objects.all(), [])
            transaction.rollback()
        finally:
            transaction.set_autocommit(True)


class FixtureTestCase(TestCase):
    def test_initial_data(self):
        "Fixtures can load initial data into models defined in packages"
        # syncdb introduces 1 initial data object from initial_data.json
        self.assertQuerysetEqual(
            Book.objects.all(), [
                'Achieving self-awareness of Python programs'
            ],
            lambda a: a.name
        )

    def test_loaddata(self):
        "Fixtures can load data into models defined in packages"
        # Load fixture 1. Single JSON file, with two objects
        management.call_command("loaddata", "fixture1.json", verbosity=0, commit=False)
        self.assertQuerysetEqual(
            Article.objects.all(), [
                "Time to reform copyright",
                "Poker has no place on ESPN",
            ],
            lambda a: a.headline,
        )

        # Load fixture 2. JSON file imported by default. Overwrites some
        # existing objects
        management.call_command("loaddata", "fixture2.json", verbosity=0, commit=False)
        self.assertQuerysetEqual(
            Article.objects.all(), [
                "Django conquers world!",
                "Copyright is fine the way it is",
                "Poker has no place on ESPN",
            ],
            lambda a: a.headline,
        )

        # Load a fixture that doesn't exist
        with warnings.catch_warnings(record=True):
            management.call_command("loaddata", "unknown.json", verbosity=0, commit=False)

        self.assertQuerysetEqual(
            Article.objects.all(), [
                "Django conquers world!",
                "Copyright is fine the way it is",
                "Poker has no place on ESPN",
            ],
            lambda a: a.headline,
        )
