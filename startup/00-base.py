import nslsii
from bluesky import RunEngine
nslsii.configure_base(
    get_ipython().user_ns,
    'chx',
    publish_documents_with_kafka=True
)

# from tiled.client import from_profile
# from databroker.v1 import Broker

# c = from_profile("chx-secure")

# db = Broker(c)

# set plot properties for 4k monitors
plt.rcParams['figure.dpi']=200

from pathlib import Path

import appdirs


try:
    from bluesky.utils import PersistentDict
except ImportError:
    import msgpack
    import msgpack_numpy
    import zict

    class PersistentDict(zict.Func):
        def __init__(self, directory):
            self._directory = directory
            self._file = zict.File(directory)
            super().__init__(self._dump, self._load, self._file)

        @property
        def directory(self):
            return self._directory

        def __repr__(self):
            return f"<{self.__class__.__name__} {dict(self)!r}>"

        @staticmethod
        def _dump(obj):
            "Encode as msgpack using numpy-aware encoder."
            # See https://github.com/msgpack/msgpack-python#string-and-binary-type
            # for more on use_bin_type.
            return msgpack.packb(
                obj,
                default=msgpack_numpy.encode,
                use_bin_type=True)

        @staticmethod
        def _load(file):
            return msgpack.unpackb(
                file,
                object_hook=msgpack_numpy.decode,
                raw=False)

runengine_metadata_dir = appdirs.user_data_dir(appname="bluesky") / Path("runengine-metadata")

# PersistentDict will create the directory if it does not exist
RE.md = PersistentDict(runengine_metadata_dir)

# send ophyd debug log to the console
# import logging
#logging.getLogger('ophyd').setLevel('DEBUG')
#console_handler = logging.StreamHandler()
#console_handler.setLevel("DEBUG")
#logging.getLogger('ophyd').addHandler(console_handler)

###############################################################################
# TODO: remove this block once https://github.com/bluesky/ophyd/pull/959 is
# merged/released.
import time
from datetime import datetime
from ophyd.signal import EpicsSignalBase, EpicsSignal, DEFAULT_CONNECTION_TIMEOUT

def print_now():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')

def wait_for_connection_base(self, timeout=DEFAULT_CONNECTION_TIMEOUT):
    '''Wait for the underlying signals to initialize or connect'''
    if timeout is DEFAULT_CONNECTION_TIMEOUT:
        timeout = self.connection_timeout
    # print(f'{print_now()}: waiting for {self.name} to connect within {timeout:.4f} s...')
    start = time.time()
    try:
        self._ensure_connected(self._read_pv, timeout=timeout)
        # print(f'{print_now()}: waited for {self.name} to connect for {time.time() - start:.4f} s.')
    except TimeoutError:
        if self._destroyed:
            raise DestroyedError('Signal has been destroyed')
        raise

def wait_for_connection(self, timeout=DEFAULT_CONNECTION_TIMEOUT):
    '''Wait for the underlying signals to initialize or connect'''
    if timeout is DEFAULT_CONNECTION_TIMEOUT:
        timeout = self.connection_timeout
    # print(f'{print_now()}: waiting for {self.name} to connect within {timeout:.4f} s...')
    start = time.time()
    self._ensure_connected(self._read_pv, self._write_pv, timeout=timeout)
    # print(f'{print_now()}: waited for {self.name} to connect for {time.time() - start:.4f} s.')

EpicsSignalBase.wait_for_connection = wait_for_connection_base
EpicsSignal.wait_for_connection = wait_for_connection
###############################################################################

from ophyd.signal import EpicsSignalBase
# EpicsSignalBase.set_default_timeout(timeout=10, connection_timeout=10)  # old style
EpicsSignalBase.set_defaults(timeout=60, connection_timeout=60)  # new style

