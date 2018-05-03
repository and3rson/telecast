import inspect

import coreapi
import coreschema
from django.conf import settings
from rest_framework.decorators import api_view, schema
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema

from telecast import codes

IGNORED_FIELDS = ['request']


def get_is_port_allowed(port):
    """
    Return TELECAST_PORTS.
    """
    if not hasattr(settings, 'TELECAST_PORTS'):
        return True
    ports = settings.TELECAST_PORTS
    if not isinstance(ports, (list, tuple)):
        ports = [ports]
    return str(port) in map(str, ports)


def method(**decorator_kwargs):
    """
    Return decorator that mimics api_view.
    """
    def decorator(func):
        """
        Decorate a method with api_view and add proper schema that matches
        function arguments and return a proxy that transforms this function
        into a callable REST endpoint.
        """
        if 'http_method_names' not in decorator_kwargs:
            decorator_kwargs['http_method_names'] = ['POST']

        @api_view(**decorator_kwargs)
        @schema(AutoSchema(manual_fields=[
            coreapi.Field(
                field,
                required=False,
                location='form',
                schema=coreschema.Anything()
            )
            for field
            in inspect.signature(func).parameters
            if field not in IGNORED_FIELDS
        ]))
        def wrapper(request, *args, **kwargs):
            """
            Proxy that wraps a function into a REST endpoint.
            """
            assert not args
            assert not kwargs
            port = request.META.get('HTTP_X_FORWARDED_PORT')
            if port and not get_is_port_allowed(port):
                return Response(dict(
                    code=codes.RPC_CODE_NOT_ALLOWED,
                    result='You are not allowed to call this TELECAST method.'
                ))

            if hasattr(request, 'data'):
                arguments = request.data
            else:
                # e. g. GET request
                arguments = {}

            try:
                result = func(request, **arguments)
            except Exception as error:
                return Response(dict(
                    code=codes.RPC_CODE_REMOTE_ERROR,
                    result=str(error)
                ))

            return Response(dict(
                code=codes.RPC_CODE_OK,
                result=result
            ))
        return wrapper
    return decorator
