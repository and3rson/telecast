import sys
import json
from uuid import UUID
import datetime

from dateutil import parser

from telecast import exceptions

# pylint: disable=invalid-name,undefined-variable
if sys.version_info > (3, 0):
    # Python 3.x
    text_type = str
    binary_type = bytes
else:
    # Python 2.x
    text_type = unicode  # noqa
    binary_type = str


class TypedJSONTranscoder(object):
    def __init__(self):
        self.encoder = json.JSONEncoder(default=self._encode_object)
        self.decoder = json.JSONDecoder(object_hook=self._decode_object)

    def encode(self, message):
        return self.encoder.encode(message)

    def _encode_object(self, v):
        print('Encode', v)
        if isinstance(v, datetime):
            return dict(__object_type='datetime', __object_value=v.isoformat())
        elif isinstance(v, UUID):
            return dict(__object_type='uuid', __object_value=v.hex)
        elif isinstance(v, binary_type):
            return dict(__object_type='binary', __object_value=list(v))
        else:
            raise exceptions.MarshallException('Don\'t know how to serialize {}'.format(repr(v)))

    def decode(self, payload):
        if isinstance(payload, binary_type):
            payload = payload.decode('utf-8')
        return self.decoder.decode(payload)

    def _decode_object(self, v):
        try:
            obj_type = v['__type']
            obj_value = v['__value']
        except Exception:
            return v

        if obj_type == 'datetime':
            return parser.parse(obj_value)
        elif obj_type == 'uuid':
            return UUID(obj_value)
        elif obj_type == 'binary':
            return bytes(bytearray(obj_value))  # Python 2.x/3.x portable method
        else:
            raise exceptions.MarshallException('Unknown type: {}'.format(obj_type))


transcoder = TypedJSONTranscoder()
