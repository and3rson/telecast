import sys
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings

from telecast.client import api_call


_executor = None


def get_executor():
    global _executor
    if _executor is None:
        if hasattr(settings, 'TELECAST_ASYNC_POOL_SIZE'):
            pool_size = settings.TELECAST_ASYNC_POOL_SIZE
        else:
            pool_size = 16
        _executor = ThreadPoolExecutor(max_workers=pool_size)
    return _executor


def _get_url(path):
    assert hasattr(settings, 'TELECAST_URL'), 'TELECAST_URL is required to perform RPC calls.'
    return settings.TELECAST_URL.rstrip('/') + '/' + path.lstrip('/')


def call(path, **kwargs):
    return api_call(_get_url(path), **kwargs)


def call_async(path, **kwargs):
    return get_executor().submit(api_call, _get_url(path), **kwargs)
