from functools import wraps

from sanic.response import json

from telecast import codes


def method():
    def decorator(fn):
        @wraps(fn)
        def wrapper(request):
            try:
                data = request.json
            except:
                data = {}
            try:
                result = fn(request, **data)
            except Exception as error:
                return json(dict(
                    code=codes.RPC_CODE_REMOTE_ERROR,
                    result=str(error)
                ))
            return json(dict(
                code=codes.RPC_CODE_OK,
                result=result
            ))
        return wrapper
    return decorator
