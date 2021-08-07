"""
memorize.py is a simple decorator for memoizing a
function across multiple program executions.

A function decorated with @memorize caches its return
value every time it is called. If the function is called
later with the same arguments, the cached value is
returned (the function is not reevaluated). The cache is
stored as a .cache file in the current directory for reuse
in future executions. If the Python file containing the
decorated function has been updated since the last run,
the current cache is deleted and a new cache is created
(in case the behavior of the function has changed).

BEWARE: only pure functions should be memoized!
Otherwise you might encounter unexpected results. Ask
yourself:
* does your function alter a global object?
* do you need to see the result of print statements?
* Does the result of your function depend on something
 outside of the application that may not behave like it
 used to (external classes, methods, functions, or data)?

DO NOT use this decorator if you are planning on
running multiple instances of the memoized function
concurrently. If there is sufficient interest this feature
may be supported in the future.

DO NOT use this decorator for functions that take
arguments that cannot be dictionary keys (such as lists).
Since the cache is stored internally as a dictionary,
no information will be cached and no memoization will
take place.

From: https://github.com/brmscheiner/memorize.py
"""
import pickle
import collections
import functools
import inspect
import os.path
import re
import unicodedata

import six

class Memorize(object):
    '''
    A function decorated with @memorize caches its return
    value every time it is called. If the function is called
    later with the same arguments, the cached value is
    returned (the function is not reevaluated). The cache is
    stored as a .cache file in the current directory for reuse
    in future executions. If the Python file containing the
    decorated function has been updated since the last run,
    the current cache is deleted and a new cache is created
    (in case the behavior of the function has changed).
    '''
    def __init__(self, folder):
        self.cache = None
        assert os.path.isdir(folder)
        self.folder = folder

    def check_cache(self):
        if self.cache is None:
            if self.cache_exists():
                try:
                    self.read_cache()  # Sets self.timestamp and self.cache
                except EOFError:
                    self.cache = {}
                else:
                    if not self.is_safe_cache():
                        self.cache = {}
            else:
                self.cache = {}

    def __call__(self, func):
        self.func = func
        function_file = inspect.getfile(func)
        self.parent_filepath = os.path.abspath(function_file)
        self.parent_filename = os.path.basename(function_file)
        self.__name__ = self.func.__name__

        def wrapped_f(*args):
            self.check_cache()
            if not isinstance(args, collections.Hashable):
                return self.func(*args)
            if args in self.cache:
                return self.cache[args]
            else:
                value = self.func(*args)
                self.cache[args] = value
                self.save_cache()
                return value

        return wrapped_f

    def get_cache_filename(self):
        """
        Sets self.cache_filename to an os-compliant
        version of "file_function.cache"
        """
        filename = _slugify(self.parent_filename.replace('.py', ''))
        funcname = _slugify(self.__name__)
        return os.path.join(self.folder, filename + '_' + funcname + '.cache')

    def get_last_update(self):
        """
        Returns the time that the parent file was last
        updated.
        """
        last_update = os.path.getmtime(self.parent_filepath)
        return last_update

    def is_safe_cache(self):
        """
        Returns True if the file containing the memoized
        function has not been updated since the cache was
        last saved.
        """
        if self.get_last_update() > self.timestamp:
            return False
        return True

    def read_cache(self):
        """
        Read a pickled dictionary into self.timestamp and
        self.cache. See self.save_cache.
        """
        with open(self.get_cache_filename(), 'rb') as f:
            data = pickle.loads(f.read())
            self.timestamp = data['timestamp']
            self.cache = data['cache']

    def save_cache(self):
        """
        Pickle the file's timestamp and the function's cache
        in a dictionary object.
        """
        with open(self.get_cache_filename(), 'wb+') as f:
            out = dict()
            out['timestamp'] = self.get_last_update()
            out['cache'] = self.cache
            f.write(pickle.dumps(out, protocol=2))

    def cache_exists(self):
        '''
        Returns True if a matching cache exists in the current directory.
        '''
        if os.path.isfile(self.get_cache_filename()):
            return True
        return False

    def __repr__(self):
        """ Return the function's docstring. """
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """ Support instance methods. """
        return functools.partial(self.__call__, obj)

def _slugify(value):
    """
    Normalizes string, converts to lowercase, removes
    non-alpha characters, and converts spaces to
    hyphens. From
    http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
    """
    value = unicodedata.normalize('NFKD', six.u(value)).encode('ascii', 'ignore')
    value = re.sub(r'[^\w\s-]', '', value.decode('utf-8', 'ignore'))
    value = value.strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value
