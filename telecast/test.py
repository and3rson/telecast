from functools import wraps
from urllib.parse import urlparse

from telecast import exceptions

try:
    from unittest.mock import patch
except ImportError:  # pragma: no cover
    from mock import patch


class FakeInvocationProxy(object):
    def __init__(self, definitions):
        self.definitions = definitions

    def __call__(self, url, **kwargs):
        path = urlparse(url).path.lstrip('/')
        assert \
            path in self.definitions, \
            'Your code tried to call path "{}" which is not present in `patch_rpc` definition.'.format(
                path
            )
        value = self.definitions[path]
        print('FakeInvocationProxy: calling {} with args {} -> {}'.format(
            path,
            repr(kwargs),
            repr(value)
        ))
        try:
            if callable(value):
                value = value(**kwargs)
        except Exception as error:
            raise exceptions.RPCRemoteError(str(error))
        return value


def patch_rpc(definitions):
    """
    Patch RPC return for specified methods.
    `definitions` should be a dictionary where each key
    is an RPC method URL and each value is a predefined
    return value or a callable.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with patch(
                'telecast.client._api_call',
                side_effect=FakeInvocationProxy(definitions)
            ):
                return fn(*args, **kwargs)
        return wrapper
    return decorator
