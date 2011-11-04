
from multiprocessing import Pool, cpu_count, current_process

try:
    import cPickle as pickle
except ImportError:
    import pickle


__all__ = ['FakeLock', 'FakeResult', 'FakePool', 'create_pool']


class FakeLock(object):

    def __init__(self):
        pass

    @staticmethod
    def acquire():
        pass

    @staticmethod
    def release():
        pass


class FakePool(object):

    def __init__(self):
        pass

    @staticmethod
    def apply_async(f, args):
        return FakeResult(apply(f, args))

    @staticmethod
    def terminate():
        pass

    @staticmethod
    def close():
        pass

    @staticmethod
    def join():
        pass


class FakeResult(object):

    def __init__(self, vals):
        self.__vals = vals

    def get(self, timeout):
        return self.__vals


def create_pool(test_instance):

    _MULTIPROCESSING = not current_process().daemon
    try:
        pickle.dumps(test_instance)
    except pickle.PicklingError:
        _MULTIPROCESSING = False

    if _MULTIPROCESSING:
        pool = Pool(cpu_count())
    else:
        pool = FakePool()

    return pool
