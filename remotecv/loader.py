import urllib2

def load(path):
    return urllib2.urlopen(path).read()
