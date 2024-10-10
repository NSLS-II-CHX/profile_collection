import nslsii
import redis

from bluesky import RunEngine
from redis_json_dict import RedisJSONDict

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

RE.md = RedisJSONDict(redis.Redis("info.chx.nsls2.bnl.gov"), prefix="")

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

assets_path = f"/nsls2/data/chx/proposals/{RE.md['cycle']}/{RE.md['data_session']}/assets/"