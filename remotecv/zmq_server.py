import time
import traceback

import zmq

from remotecv.app import RemoteCvApp
from remotecv.utils import logger

def run_server(host, port):
    app = RemoteCvApp()
    context = zmq.Context()
    rep = context.socket(zmq.REP)
    bind_address = 'tcp://%s:%s' % (host, port)

    logger.debug('listening to connections at %s' % bind_address)

    rep.bind(bind_address)
    while True:
        result = ''
        msg = rep.recv()
        try:
            start_time = time.time()
            logger.debug('Accepting message')
            result = app.process_request(msg)
        except:
            logger.error(traceback.format_exc())

        rep.send(result)
        logger.debug('Sending response. Ellapsed: %d' % ((time.time() - start_time) * 1000))
