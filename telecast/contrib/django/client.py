from django.conf import settings

from telecast.client import api_call


def call(path, **kwargs):
    assert hasattr(settings, 'TELECAST_URL'), 'TELECAST_URL is required to perform RPC calls.'
    url = settings.TELECAST_URL.rstrip('/') + '/' + path.lstrip('/')
    return api_call(url, **kwargs)
