import nslsii
import redis

from bluesky import RunEngine
from pathlib import Path
from redis_json_dict import RedisJSONDict
from tiled.client import from_profile

nslsii.configure_base(
    get_ipython().user_ns,
    'chx',
    publish_documents_with_kafka=True
)

# set plot properties for 4k monitors
plt.rcParams['figure.dpi']=200

# Set the metadata dictionary
RE.md = RedisJSONDict(redis.Redis("info.chx.nsls2.bnl.gov"), prefix="")

from ophyd.signal import EpicsSignalBase
EpicsSignalBase.set_defaults(timeout=60, connection_timeout=60)  # new style

assets_path = f"/nsls2/data/chx/proposals/{RE.md['cycle']}/{RE.md['data_session']}/assets/"