import urllib2

def load_sync(path):
    return urllib2.urlopen(path).read()
