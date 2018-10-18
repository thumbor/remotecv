import urllib2
import re

def load_sync(path):
    if not re.match(r'^http?', path):
        path = 'https://%s' % path
    path = urllib2.unquote(path)
    return urllib2.urlopen(path).read()
