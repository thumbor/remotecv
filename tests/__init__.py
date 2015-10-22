from os.path import join, dirname


def read_fixture(path):
    with open(join(dirname(__file__), 'fixtures', path)) as f:
        return f.read()
