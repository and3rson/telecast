from json import dumps, loads
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from telecast.exceptions import RPCError


def api_call(url, **kwargs):
    request = Request(url, dumps(kwargs).encode(), headers={
        'Content-Type': 'application/json'
    })
    try:
        response = urlopen(request)
    except HTTPError as error:
        data = error.read()
        try:
            error = loads(data)['detail']
        except:
            error = str(data)
        raise RPCError(error)
    except URLError as error:
        raise RPCError(str(error))
    else:
        data = response.read()
        try:
            result = loads(data)['result']
        except:
            raise RPCError(str(data))
        else:
            return result
