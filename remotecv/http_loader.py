import urllib2
import re

def load_sync(path):
    if not re.match(r'^https?', path):
        path = 'http://%s' % path
    return urllib2.urlopen(path).read()
