import asyncio
from aiohttp import web
from functools import partial
from .endpoint import Endpoint
from .helpers import STICKER


class Metaclass(type):

    # Public

    def __new__(cls, name, bases, attrs):
        cls = type.__new__(cls, name, bases, attrs)
        cls.Request = web.Request
        cls.StreamResponse = web.StreamResponse
        cls.Response = web.Response
        cls.WebSocketResponse = web.WebSocketResponse
        for name, obj in vars(web).items():
            if name.startswith('HTTP'):
                name = name.replace('HTTP', '', 1)
                setattr(cls, name, obj)
        return cls


class http(metaclass=Metaclass):
    """Adapter between Interst and aiohttp and binding maker.

    Naming: aiohttp.web.HTTP* -> http.*

    *under development*

    .. seealso:: http://aiohttp.readthedocs.org/en/
    """

    # Public

    @classmethod
    def bind(cls, param):
        return cls.__process(param)

    @classmethod
    def get(cls, param):
        """Bind a get responder.
        """
        return cls.__process(param, methods=['GET'])

    @classmethod
    def post(cls, param):
        """Bind a post responder.
        """
        return cls.__process(param, methods=['POST'])

    @classmethod
    def put(cls, param):
        """Bind a put responder.
        """
        return cls.__process(param, methods=['PUT'])

    @classmethod
    def delete(cls, param):
        """Bind a delete responder.
        """
        return cls.__process(param, methods=['DELETE'])

    @classmethod
    def patch(cls, param):
        """Bind a patch responder.
        """
        return cls.__process(param, methods=['PATCH'])

    @classmethod
    def head(cls, param):
        """Bind a head responder.
        """
        return cls.__process(param, methods=['HEAD'])

    @classmethod
    def options(cls, param):
        """Bind a options responder.
        """
        return cls.__process(param, methods=['OPTIONS'])

    # Private

    @classmethod
    def __process(cls, param, *, methods=None):
        if isinstance(param, str):
            return partial(cls.__register, path=param, methods=methods)
        return cls.__register(param, methods=methods)

    @classmethod
    def __register(cls, function, **kwargs):
        if not asyncio.iscoroutine(function):
            function = asyncio.coroutine(function)
        endpoint = kwargs.pop('endpoint', Endpoint)
        factory = partial(endpoint, **kwargs)
        setattr(function, STICKER, factory)
        return function
