import sys
import json
import asyncio
import logging
from interest import Service, Middleware, Logger, Handler, http


class Restful(Middleware):

    # Public

    @asyncio.coroutine
    def process(self, request):
        try:
            response = http.Response()
            payload = yield from self.next(request)
        except http.Exception as exception:
            response = exception
            payload = {'message': str(response)}
        response.text = json.dumps(payload)
        response.content_type = 'application/json'
        return response


class Session(Middleware):

    # Public

    @asyncio.coroutine
    def process(self, request):
        assert self.main == self.service.over
        assert self.over == self.service
        assert self.prev == self.service['restful']
        assert self.next == self.service['comment']
        assert self.next == self.service['comment']['read'].over
        request.user = False
        response = yield from self.next(request)
        return response


class Auth(Middleware):

    # Public

    METHODS = ['POST']

    @asyncio.coroutine
    def process(self, request):
        assert self.service.match(request, root='/api/v1')
        assert self.service.match(request, path=request.path)
        assert self.service.match(request, methods=['POST'])
        if not request.user:
            raise http.Unauthorized()
        response = yield from self.next(request)
        return response


class Comment(Middleware):

    # Public

    PREFIX = '/comment'
    MIDDLEWARES = [Auth]

    @http.get('/key=<key:int>')
    def read(self, request, key):
        url = '/api/v1/comment/key=' + str(key)
        assert url == self.service.url('comment.read', key=key)
        assert url == self.service.url('read', base=self, key=key)
        return {'key': key}

    @http.put
    @http.post  # Endpoint's behind the Auth
    def upsert(self, request):
        self.service.log('info', 'Adding custom header!')
        raise http.Created(headers={'endpoint': 'upsert'})


# Create restful service
restful = Service(
    prefix='/api/v1',
    middlewares=[Restful, Session, Comment])

# Create main service
service = Service(
    logger=Logger.config(
        template='%(request)s | %(status)s | %(<endpoint:res>)s'),
    handler=Handler.config(
        connection_timeout=25, request_timeout=5))

# Add restful to main
service.push(restful)

# Listen forever
argv = dict(enumerate(sys.argv))
logging.basicConfig(level=logging.DEBUG)
service.listen(host=argv.get(1, '127.0.0.1'), port=argv.get(2, 9000))
