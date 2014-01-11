"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import unittest
from django.test.client import Client
from django.test import Client, TestCase
from django.contrib.auth import authenticate
from django.contrib.auth.models import *
from django.core import mail
import datetime
import time

from django.test import TestCase


class SimpleTest(TestCase):
    fixtures = ['f1.json']
    # Every test needs a client

    def setUp(self):
        self.client = Client()

    def test_create_auction(self):
        # Test the create auction view to check if it is working
        response = self.client.get('/createauctionConf/')
        self.failUnlessEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/createauctionConf/')

        # Create a user to try to login to see if login is working correctly
        user = User.objects.create_user(username = 'admin1', email='dummy@dummy.com', password = 'testing')
        uid = user.id
        user.is_staff = True
        user.save()

        print " test your login id"

        login = self.client.login(username='admin1', password='testing')
        self.failUnless(login, True)
        self.assertEqual(login, True)


        EndDate = datetime.datetime(2010, 06, 04, 3, 45, 50)

        post_data = {
            'title': 'Title1',
            'desc': 'description',
            'category': 'electronics',
            'start-date': datetime.datetime.now(),
            'end_date': EndDate,
            'seller': user.id,
            'price': 60,
            'banned': False,


        }

        r = self.client.post('/createauctionConf/', post_data)
        self.failUnlessEqual(r.status_code, 200)


        # This is the test for bid UC6
    def test_view_auction_event(self):
        # Test bid view which is the view_auction_event
        response = self.client.get('/view_auction_event/1/')
        self.failUnlessEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/view_auction_event/1/')

        # Create a user and login to view and bid on the current auction event
        user1 = User.objects.create_user(username = 'admin2', email='dummy@dummy.com', password = 'testing2')
        uid = user1.id
        user1.is_staff = True
        user1.save()

        print " test your login id"

        login = self.client.login(username='admin2', password='testing2')
        self.failUnless(login, True)
        self.assertEqual(login, True)

        # Testing the bid form that it works correctly
        response = self.client.get('/view_auction_event/1/')
        self.assertFalse(response.context['form'].is_valid())


    def test_edit_description(self):
        # Test the edit description support for multiple current sessions
        response = self.client.get('/auction/Samsung/edit')
        self.assertEqual(response.status_code, 301)







