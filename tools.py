import traceback
import urllib
import urllib2
import time
import sys


class LudiException(Exception):
    pass


def retry(howmany):
    def try_it(func):
        def f(*args, **kwargs):
            attempts = 0
            while attempts <= howmany:
                try:
                    return func(*args, **kwargs)
                except:
                    attempts += 1
                    if attempts > howmany:
                        raise
                    time.sleep(1)

        return f

    return try_it


@retry(5)
def urlopen(*args, **kwargs):
    return urllib.urlopen(*args, **kwargs)


@retry(5)
def urlopen2(*args, **kwargs):
    return urllib2.urlopen(*args, **kwargs)


def strip_newline(word):
    if word[-1] == '\n' or word[-1] == '\r':
        return word[:-1]
    else:
        return word


def strip_indicators(word):
    if word and word[0] in ".*/\\":
        return word[1:]
    else:
        return word


def split_to_chunks(l, n):
        for i in xrange(0, len(l), n):
            yield l[i:i+n]


def remote_ex(f):
    def v(*args, **kw):
        res = None

        try:
            res = f(*args, **kw)
            return {'result': res}
        except Exception as e:
            type, error, uu = sys.exc_info()
            w = {'error': (type, error, traceback.format_exc())}
            return w
    v.__doc__ = f.__doc__
    v.__dict__.update(f.__dict__)
    v.__name__ = f.__name__
    v.__module__ = f.__module__
    return v

