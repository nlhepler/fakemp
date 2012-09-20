
from __future__ import division, print_function

import logging

from multiprocessing import Pool, cpu_count, current_process
from os import getenv
from sys import exc_info, exit as sys_exit

from six.moves import cPickle as pickle


__all__ = [
    'FAKEMP_LOGGER',
    'FakeLock',
    'FakeResult',
    'FakePool',
    'create_pool',
    'farmout',
    'farmworker'
]

__version__ = '0.9.2'

FAKEMP_LOGGER = '2dTXjMDeFheXx5QjWZmz8XHz'

_ncpu = None


def _setup_log():
    h = logging.StreamHandler()
    f = logging.Formatter('%(levelname)s %(asctime)s %(process)d FAKEMP %(funcName)s: %(message)s')
    h.setFormatter(f)
    logging.getLogger(FAKEMP_LOGGER).addHandler(h)
_setup_log()


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
        return FakeResult(f(*args))

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

    def get(self, timeout=0xFFFF):
        return self.__vals


def create_pool(pickletest):
    global _ncpu

    log = logging.getLogger(FAKEMP_LOGGER)

    if _ncpu is None:
        var = getenv('NCPU', 'auto').lower().strip()

        try:
            _ncpu = cpu_count() if var == 'auto' else min(cpu_count(), int(var))
        except ValueError:
            _ncpu = 0

        if _ncpu < 2:
            log.debug('multiprocessing disabled at request of NCPU environment var')

    ncpu = 0 if current_process().daemon else _ncpu

    if ncpu < 2:
        pass
    elif pickletest is False:
        ncpu = 0
        log.debug('multiprocessing disabled at request of caller')
    else:
        try:
            pickle.dumps(pickletest)
        except pickle.PicklingError:
            ncpu = 0
            log.debug('multiprocessing disabled because pickle cannot handle given objects')

    # don't bother spawning a single process,
    # just keep the whole thing single-threaded
    if ncpu > 1:
        pool = Pool(ncpu)
    else:
        pool = FakePool()

    return pool


def farmout(num, setup, worker, isresult, attempts=3, pickletest=None):
    try:
        if pickletest is None:
            pickletest = worker
        results = [None] * num
        undone = range(num)
        for _ in range(attempts):
            pool = create_pool(pickletest)

            for i in undone:
                results[i] = pool.apply_async(worker, setup(i))

            pool.close()
            pool.join()

            for i in undone:
                results[i] = results[i].get(0xFFFF)

            if any([isinstance(r, KeyboardInterrupt) for r in results]):
                raise KeyboardInterrupt
            else:
                undone = [i for i, r in enumerate(results) if not isresult(r)]
                if not len(undone):
                    break

        excs = [e for e in results if isinstance(e, Exception)]
        if len(excs):
            raise excs[0]

        if not all([isresult(r) for r in results]):
            raise RuntimeError("Random and unknown weirdness happened while trying to farm out work to child processes")

        return results

    except KeyboardInterrupt as e:
        if pool is not None:
            pool.terminate()
            pool.join()
        if current_process().daemon:
            return e
        else:
            print('caught ^C (keyboard interrupt), exiting ...')
            sys_exit(-1)


def farmworker(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except KeyboardInterrupt:
        return KeyboardInterrupt
    except:
        # XXX this is just a hack to get around the fact we can't ask the environment
        # for NCPU directly
        if current_process().daemon:
            return exc_info()[1]
        else:
            raise
