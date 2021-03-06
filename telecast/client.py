from json import dumps, loads
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from telecast import exceptions, codes
from telecast.marshalling import transcoder


def api_call(url, **kwargs):
    # This is a proxy method to make mocking easier.
    # The reason for this is that api_call can be imported anywhere
    # while _api_call will always be used only from within this module.
    return _api_call(url, **kwargs)


def _api_call(url, **kwargs):
    request = Request(url, transcoder.encode(kwargs).encode(), headers={
        'Content-Type': 'application/json'
    })
    try:
        response = urlopen(request)
        data = response.read()
        status = response.status
    except HTTPError as error:
        data = error.read()
        status = error.code
    except URLError as error:
        raise exceptions.RPCProtocolError(str(error))

    if status != 200:
        raise exceptions.RPCProtocolError('HTTP ' + str(status) + ': ' + str(data))

    try:
        data = loads(data)
        result = data['result']
        code = data['code']
    except Exception as error:
        raise exceptions.RPCProtocolError(str(error))
    else:
        if code == codes.RPC_CODE_PROTOCOL_ERROR:
            # Not used at the moment.
            raise exceptions.RPCProtocolError(str(result))
        if code == codes.RPC_CODE_NOT_ALLOWED:
            raise exceptions.RPCNotAllowedError(str(result))
        if code == codes.RPC_CODE_REMOTE_ERROR:
            raise exceptions.RPCRemoteError(str(result))
        return result
