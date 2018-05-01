from django.conf import settings

from telecast.client import api_call


def call(path, **kwargs):
    assert hasattr(settings, 'RPC_URL'), 'RPC_URL is required to perform RPC calls.'
    url = settings.RPC_URL.rstrip('/') + '/' + path.lstrip('/')
    return api_call(url, **kwargs)
