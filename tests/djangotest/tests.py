from json import dumps, loads
import os
from urllib.parse import urlparse

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangotest.settings')

django.setup()

from django.test import LiveServerTestCase, Client
from django.conf import settings

from telecast.contrib.django.client import call, call_async
from telecast.test import patch_rpc
from telecast import exceptions


class Test(LiveServerTestCase):
    def setUp(self):
        self.client = Client()

    def test_disallowed_method_def_405_error(self):
        response = self.client.get('/add')
        self.assertEqual(response.status_code, 405)

    def test_bad_payload_400_error(self):
        response = self.client.post(
            '/add',
            'can i haz jsonz',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = loads(response.content)
        self.assertIn('result', data)
        self.assertIn('Bad payload.', data['result'])

    def test_raw_call(self):
        response = self.client.post('/add')
        self.assertEqual(response.status_code, 415)

        response = self.client.post(
            '/add',
            dumps(dict(a=1, b=2)),
            content_type='application/json'
        )
        self.assertEqual(loads(response.content), dict(code=120, result=3))

        response = self.client.get(
            '/foo'
        )
        self.assertEqual(loads(response.content), dict(code=120, result='bar'))

        response = self.client.post(
            '/add',
            content_type='application/json'
        )
        self.assertEqual(loads(response.content), dict(
            code=150,
            result='add() missing 2 required positional arguments: \'a\' and \'b\''
        ))

    def test_rpc_call(self):
        try:
            settings.TELECAST_URL = self.live_server_url
            result = call('/add', a=1, b=2)
            self.assertEqual(result, 3)
            result = call('/add', a=[1], b=['2'])
            self.assertEqual(result, [1, '2'])

            result = call('/hello')
            self.assertEqual(result, 'Hello, stranger!')
            result = call('/hello', name='Dolly')
            self.assertEqual(result, 'Hello, Dolly!')
        finally:
            del settings.TELECAST_URL

    def test_call_async(self):
        try:
            settings.TELECAST_URL = self.live_server_url
            future = call_async('/add', a=1, b=2)
            self.assertEqual(future.result(), 3)

            future = call_async('/add', a=1, b='2')
            self.assertRaises(exceptions.RPCRemoteError, lambda: future.result())
        finally:
            del settings.TELECAST_URL

    def test_internal_error(self):
        try:
            settings.TELECAST_URL = self.live_server_url
            self.assertRaises(exceptions.RPCRemoteError, lambda: call('/add', a=1, b='2'))
        finally:
            del settings.TELECAST_URL

    def test_bad_response(self):
        try:
            settings.TELECAST_URL = self.live_server_url
            self.assertRaises(exceptions.RPCProtocolError, lambda: call('/just-a-view'))
        finally:
            del settings.TELECAST_URL

    def test_misconfiguration(self):
        self.assertRaises(AssertionError, lambda: call('/add', a=[1], b=['2']))
        try:
            settings.TELECAST_URL = 'http://666.666.666.666/'
            self.assertRaises(exceptions.RPCProtocolError, lambda: call('/add', a=[1], b=['2']))
        finally:
            del settings.TELECAST_URL

    def test_allowed_ports(self):
        try:
            settings.TELECAST_URL = self.live_server_url

            settings.TELECAST_PORTS = ['4242']
            # Emulate calls from reverse proxy
            response = self.client.get('/foo', **{
                'HTTP_X_FORWARDED_PORT': '4242'
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(loads(response.content)['code'], 120)
            self.assertEqual(call('/add', a=1, b=2), 3)

            response = self.client.get('/foo', **{
                'HTTP_X_FORWARDED_PORT': '4243'
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(loads(response.content)['code'], 145)
            # self.assertRaises(exceptions.RPCNotAllowedError, lambda: call('/add', a=1, b=2))

            del settings.TELECAST_PORTS
            response = self.client.get('/foo', **{
                'HTTP_X_FORWARDED_PORT': '4243'
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(loads(response.content)['code'], 120)
            self.assertEqual(call('/add', a=1, b=2), 3)

        finally:
            del settings.TELECAST_URL
            try:
                del settings.TELECAST_PORTS
            except:
                pass

    @patch_rpc({
        'new/mul': lambda a, b: a * b,
        'new/the-answer': 42,
        'new/error': lambda: 1 / 0
    })
    def test_mock_usage(self):
        try:
            settings.TELECAST_URL = 'foo://bar'  # required to properly parse URL.
            self.assertEqual(call('new/mul', a=3, b=4), 12)
            self.assertEqual(call('new/the-answer'), 42)
            self.assertRaises(exceptions.RPCRemoteError, lambda: call('new/error'))
        finally:
            del settings.TELECAST_URL

    @patch_rpc({'/unused': None})
    def test_mock_misusage(self):
        try:
            settings.TELECAST_URL = 'foo://bar'  # required to properly parse URL.
            self.assertRaises(AssertionError, lambda: call('/add', a=3, b=4))
        finally:
            del settings.TELECAST_URL
