from json import dumps, loads
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangotest.settings')

django.setup()

from django.test import LiveServerTestCase, Client
from django.conf import settings

from telecast.contrib.django.client import call
from telecast.exceptions import RPCError


class Test(LiveServerTestCase):
    def setUp(self):
        self.client = Client()

    def test_disallowed_method(self):
        response = self.client.get('/add')
        self.assertEqual(response.status_code, 405)

    def test_bad_payload(self):
        response = self.client.post(
            '/add',
            'can i haz jsonz',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = loads(response.content)
        self.assertIn('detail', data)
        self.assertIn('JSON parse error', data['detail'])

    def test_raw_call(self):
        response = self.client.post('/add')
        self.assertEqual(response.status_code, 500)

        response = self.client.post(
            '/add',
            dumps(dict(a=1, b=2)),
            content_type='application/json'
        )
        self.assertEqual(loads(response.content), dict(result=3))

        response = self.client.get(
            '/foo'
        )
        self.assertEqual(loads(response.content), dict(result='bar'))

        response = self.client.post(
            '/add',
            content_type='application/json'
        )
        self.assertEqual(loads(response.content), dict(
            detail='add() missing 2 required positional arguments: \'a\' and \'b\''
        ))

    def test_rpc_call(self):
        try:
            settings.RPC_URL = self.live_server_url
            result = call('/add', a=1, b=2)
            self.assertEqual(result, 3)
            result = call('/add', a=[1], b=['2'])
            self.assertEqual(result, [1, '2'])

            result = call('/hello')
            self.assertEqual(result, 'Hello, stranger!')
            result = call('/hello', name='Dolly')
            self.assertEqual(result, 'Hello, Dolly!')
        finally:
            del settings.RPC_URL

    def test_internal_error(self):
        try:
            settings.RPC_URL = self.live_server_url
            self.assertRaises(RPCError, lambda: call('/add', a=1, b='2'))
        finally:
            del settings.RPC_URL

    def test_bad_response(self):
        try:
            settings.RPC_URL = self.live_server_url
            self.assertRaises(RPCError, lambda: call('/just-a-view'))
        finally:
            del settings.RPC_URL

    def test_misconfiguration(self):
        self.assertRaises(AssertionError, lambda: call('/add', a=[1], b=['2']))
        try:
            settings.RPC_URL = 'http://666.666.666.666/'
            self.assertRaises(RPCError, lambda: call('/add', a=[1], b=['2']))
        finally:
            del settings.RPC_URL
