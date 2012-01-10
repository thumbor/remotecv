from tornado.web import RequestHandler, Application
from tornado import httpserver, ioloop

from remotecv.app import RemoteCvApp
from remotecv.utils import logger

class RemoteCvProcessHandler(RequestHandler):
    remote_cv_app = RemoteCvApp()

    def post(self):
        data = self.request.body
        result = self.remote_cv_app.process_request(data)
        self.write(result)


class RemoteCvTornadoApp(Application):
    def __init__(self):
        handlers = [
            (r'/handle_image', RemoteCvProcessHandler)
        ]
        super(RemoteCvTornadoApp, self).__init__(handlers)


def run_server(host, port):
    application = RemoteCvTornadoApp()
    if host == '*':
        host = '0.0.0.0'

    logger.debug('listening to connections at http://%s:%d' % (host, port))

    server = httpserver.HTTPServer(application)
    server.bind(port, host)
    server.start(1)

    ioloop.IOLoop.instance().start()

