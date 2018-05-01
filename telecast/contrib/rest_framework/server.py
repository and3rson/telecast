import inspect

import coreapi
import coreschema
from rest_framework.exceptions import APIException
from rest_framework.decorators import api_view, schema
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema

IGNORED_FIELDS = ['request']


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
            if hasattr(request, 'data'):
                arguments = request.data
            else:
                # e. g. GET request
                arguments = {}

            try:
                result = func(request, **arguments)
            except Exception as error:
                result = error

            if isinstance(result, Exception):
                raise APIException(dict(
                    detail=str(result)
                ))
            return Response(dict(
                result=result
            ))
        return wrapper
    return decorator
