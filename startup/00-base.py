import nslsii
import redis

from bluesky import RunEngine
from pathlib import Path
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

RE.md = RedisJSONDict(redis.Redis("info.chx.nsls2.bnl.gov"), prefix="")

# send ophyd debug log to the console
# import logging
#logging.getLogger('ophyd').setLevel('DEBUG')
#console_handler = logging.StreamHandler()
#console_handler.setLevel("DEBUG")
#logging.getLogger('ophyd').addHandler(console_handler)

from ophyd.signal import EpicsSignalBase
EpicsSignalBase.set_defaults(timeout=60, connection_timeout=60)  # new style

assets_path = f"/nsls2/data/chx/proposals/{RE.md['cycle']}/{RE.md['data_session']}/assets/"