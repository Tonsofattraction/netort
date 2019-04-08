import re
import sys
from importlib.abc import PathEntryFinder
from importlib.util import spec_from_loader
import requests


def url_hook(url):
    url, filename = url.rsplit('/', 1)
    filename = re.sub('\.py$', '', filename)
    if not url.startswith(('http', 'https')):
        raise ImportError
    return URLFinder(url, filename)


class URLFinder(PathEntryFinder):
    def __init__(self, url, filename):
        self.url = url
        self.filename = filename

    def find_spec(self, name, target=None):
        if name == self.filename:
            origin = self.url
            loader = URLLoader()
            return spec_from_loader(name, loader, origin=origin)
        else:
            return None


class URLLoader:

    def create_module(self, target):
        return None

    def exec_module(self, module):
        source = requests.get(module.__spec__.origin).content
        code = compile(source, module.__spec__.origin, mode="exec")
        exec(code, module.__dict__)


def make_importable(url):
    """

    :param url: str. must lead to downloadable python module the name of the module will be a subject of import

    make_importable('http://filepile.org/download?name=megamodule.py')
    import megamodule

    """
    if not url_hook in sys.path_hooks:
        sys.path_hooks.append(url_hook)
    sys.path.append(url)
